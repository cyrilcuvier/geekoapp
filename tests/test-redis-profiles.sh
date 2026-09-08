#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
chart="$repo_root/helm/geeko"
docker_values="$chart/values-demo-dockerhub.yaml"
appco_values="$chart/values-demo-appco.yaml"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT

render_geeko() {
  local values_file="$1"
  local output_file="$2"
  shift 2
  helm template geeko "$chart" -f "$values_file" "$@" > "$output_file"
}

assert_contains() {
  local file="$1"
  local text="$2"
  if ! grep -Fq -- "$text" "$file"; then
    printf 'expected %s to contain: %s\n' "$file" "$text" >&2
    exit 1
  fi
}

assert_not_contains() {
  local file="$1"
  local text="$2"
  if grep -Fq -- "$text" "$file"; then
    printf 'expected %s not to contain: %s\n' "$file" "$text" >&2
    exit 1
  fi
}

# No Redis authentication setting belongs in either demo profile or the chart defaults.
if grep -Fq -- 'redisSecret' "$docker_values" "$appco_values" "$chart/values.yaml"; then
  printf 'Redis Secret configuration unexpectedly remains in demo values\n' >&2
  exit 1
fi

# State A: the baseline contains the bundled Docker Hub Redis and no Redis Secret reference.
render_geeko "$docker_values" "$tmp_dir/dockerhub-1.yaml"
assert_contains "$tmp_dir/dockerhub-1.yaml" 'name: geeko-redis'
assert_contains "$tmp_dir/dockerhub-1.yaml" 'image: "redis:8.6.4"'
assert_contains "$tmp_dir/dockerhub-1.yaml" 'value: "redis://geeko-redis:6379/0"'
assert_not_contains "$tmp_dir/dockerhub-1.yaml" 'name: geeko-redis-auth'

# State B: geekoapp stops deploying Redis and uses the unauthenticated AppCo service URL.
render_geeko "$appco_values" "$tmp_dir/appco-geeko.yaml"
assert_not_contains "$tmp_dir/appco-geeko.yaml" 'app: geeko-redis'
assert_not_contains "$tmp_dir/appco-geeko.yaml" 'image: "redis:8.6.4"'
assert_contains "$tmp_dir/appco-geeko.yaml" 'value: "redis://geeko-appco-redis:6379/0"'
assert_not_contains "$tmp_dir/appco-geeko.yaml" 'secretKeyRef:'

# Safe rollback step 1: recreate Docker Hub Redis while API still uses AppCo.
render_geeko "$appco_values" "$tmp_dir/rollback-stage.yaml" --set redis.source=dockerhub
assert_contains "$tmp_dir/rollback-stage.yaml" 'image: "redis:8.6.4"'
assert_contains "$tmp_dir/rollback-stage.yaml" 'value: "redis://geeko-appco-redis:6379/0"'
assert_not_contains "$tmp_dir/rollback-stage.yaml" 'secretKeyRef:'

# Safe rollback step 2: switch API back; State A is byte-for-byte reproducible.
render_geeko "$docker_values" "$tmp_dir/dockerhub-2.yaml"
cmp "$tmp_dir/dockerhub-1.yaml" "$tmp_dir/dockerhub-2.yaml"

# A typo must fail closed instead of silently removing the bundled Redis.
if helm template geeko "$chart" --set redis.source=typo > /dev/null 2>&1; then
  printf 'invalid redis.source unexpectedly rendered successfully\n' >&2
  exit 1
fi

# AppCo mode must never render with the stale Docker Hub service URL.
if helm template geeko "$chart" --set redis.source=appco > /dev/null 2>&1; then
  printf 'appco mode without its AppCo URL unexpectedly rendered successfully\n' >&2
  exit 1
fi

# Docker Hub mode permits only the baseline URL or the staged rollback AppCo URL.
for invalid_url in '' 'redis://unexpected.example:6379/0'; do
  if helm template geeko "$chart" --set-string "api.redisUrl=$invalid_url" > /dev/null 2>&1; then
    printf 'dockerhub mode accepted invalid Redis URL: %s\n' "$invalid_url" >&2
    exit 1
  fi
done

printf 'redis profile render tests: PASS\n'
