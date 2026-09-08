#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
appco_values="$repo_root/demo/redis-appco-values.yaml"
tmp_dir="$(mktemp -d)"
trap 'rm -rf "$tmp_dir"' EXIT
render="$tmp_dir/appco-redis.yaml"

assert_contains() {
  local text="$1"
  if ! grep -Fq -- "$text" "$render"; then
    printf 'expected AppCo render to contain: %s\n' "$text" >&2
    exit 1
  fi
}

helm template geeko-appco oci://dp.apps.rancher.io/charts/redis \
  --version 2.7.2 \
  -f "$appco_values" > "$render"

assert_contains 'name: geeko-appco-redis'
assert_contains 'image: dp.apps.rancher.io/containers/redis:8.6.6-9.11'
assert_contains 'name: application-collection'

# Ignore upstream formatting differences such as optional YAML quotes.
if ! grep -Eq "name: ['\"]?geeko-redis-auth['\"]?$" "$render"; then
  printf 'AppCo render does not reference Secret geeko-redis-auth\n' >&2
  exit 1
fi
if ! grep -Eq "key: ['\"]?password['\"]?$" "$render"; then
  printf 'AppCo render does not reference Secret key password\n' >&2
  exit 1
fi

if grep -Fq -- 'kind: Secret' "$render"; then
  printf 'AppCo chart unexpectedly rendered a Secret\n' >&2
  exit 1
fi

printf 'Redis AppCo authenticated integration render: PASS\n'
