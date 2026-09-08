# Redis supply-chain demo

This directory defines the Redis Application Collection release used by the
`geekoapp` target state. The geeko chart keeps two explicit profiles:

- `helm/geeko/values-demo-dockerhub.yaml`: reproducible baseline using
  `redis:8.6.4` and Service `geeko-redis`.
- `helm/geeko/values-demo-appco.yaml`: geekoapp uses the separate Redis release
  through a Kubernetes Secret.

The baseline intentionally pins the requested Docker Hub tag `redis:8.6.4`.
This makes the declared demo state repeatable, but it is not byte-level image
immutability: that would additionally require a validated multi-architecture
digest.

No credential is stored in this repository. Before the target-state commands,
create these namespace-local Secrets through Rancher or another approved
out-of-band mechanism:

- `application-collection`: registry pull credential for
  `dp.apps.rancher.io`.
- `geeko-redis-auth`, with two keys:
  - `password`: the Redis password consumed by the AppCo chart.
  - `url`: the complete matching URL consumed by geeko-api,
    `redis://:<same-password>@geeko-appco-redis:6379/0`.

## Show the current declared state

```sh
helm get values geeko -n <namespace>
helm get values geeko-appco -n <namespace>  # only when the AppCo release exists
```

## A. Establish or restore the Docker Hub baseline

```sh
helm upgrade --install geeko ./helm/geeko \
  -n <namespace> --create-namespace \
  -f ./helm/geeko/values-demo-dockerhub.yaml
```

Expected endpoint: `redis://geeko-redis:6379/0`.

## B. Switch to Application Collection

Install and validate Redis before switching geekoapp, so the API is never
pointed at an unavailable target:

```sh
helm upgrade --install geeko-appco \
  oci://dp.apps.rancher.io/charts/redis \
  --version 2.7.2 \
  -n <namespace> \
  -f ./demo/redis-appco-values.yaml

kubectl rollout status statefulset/geeko-appco-redis -n <namespace>

helm upgrade --install geeko ./helm/geeko \
  -n <namespace> \
  -f ./helm/geeko/values-demo-appco.yaml
```

Expected Service: `geeko-appco-redis`. The password remains in the Secret;
Helm values contain only its name and key.

## Return to A

Rollback order is deliberate:

1. Recreate `geeko-redis` while geeko-api still uses AppCo.
2. Wait for the Docker Hub Redis deployment.
3. Apply the Docker Hub profile to reconnect geeko-api.
4. Validate geekoapp.
5. Only then remove the separate AppCo release.

```sh
helm upgrade --install geeko ./helm/geeko \
  -n <namespace> \
  -f ./helm/geeko/values-demo-appco.yaml \
  --set redis.source=dockerhub

kubectl rollout status deployment/geeko-redis -n <namespace>

helm upgrade --install geeko ./helm/geeko \
  -n <namespace> \
  -f ./helm/geeko/values-demo-dockerhub.yaml

kubectl rollout status deployment/geeko-api -n <namespace>

# In another terminal, verify a Redis-backed API request before removing AppCo:
kubectl port-forward service/geeko-api 8000:8000 -n <namespace>
curl --fail http://127.0.0.1:8000/api/geeko

helm uninstall geeko-appco -n <namespace>
```

The same transition can be represented by a PR and reversed by reverting that
PR or merging an inverse PR. No manual edit of live Kubernetes resources is
needed.

## Local render test

The geekoapp profile test is hermetic and requires no registry login:

```sh
./tests/test-redis-profiles.sh
```

The separate AppCo integration test pulls the pinned private chart. Run it
only after an out-of-band `helm registry login dp.apps.rancher.io`:

```sh
./tests/test-redis-appco-integration.sh
```
