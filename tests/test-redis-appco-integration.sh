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

if grep -Fq -- 'kind: Secret' "$render"; then
  printf 'AppCo chart unexpectedly rendered a Secret\n' >&2
  exit 1
fi
if grep -Fq -- 'geeko-redis-auth' "$render"; then
  printf 'AppCo chart unexpectedly references a Redis auth Secret\n' >&2
  exit 1
fi
if grep -Fq -- 'application-collection' "$render"; then
  printf 'AppCo values unexpectedly reference an explicit image pull Secret\n' >&2
  exit 1
fi
if grep -Fq -- 'imagePullSecrets:' "$render"; then
  printf 'AppCo pod unexpectedly declares explicit imagePullSecrets\n' >&2
  exit 1
fi
if grep -Fq -- 'name: _REDIS_PASSWORD' "$render"; then
  printf 'AppCo chart unexpectedly injects a Redis password environment variable\n' >&2
  exit 1
fi
if grep -Fq -- 'name: REDISCLI_AUTH' "$render"; then
  printf 'AppCo chart unexpectedly injects Redis client authentication\n' >&2
  exit 1
fi

printf 'Redis AppCo unauthenticated integration render: PASS\n'
