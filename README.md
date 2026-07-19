# Où est Geeko ?

A small cloud-native demo app built around SUSE's chameleon mascot, Geeko. It exists to demonstrate,
end to end, a set of real infrastructure patterns (Helm/Kubernetes deployment, a deliberately
insecure vs. hardened dependency, and a legacy service reachable over a private tunnel) rather than
to be a "real" product.

## What it does

Geeko wanders around an arena, changes color/mood, and occasionally reports a "fortune" from a
separate legacy service ("Le Sage de Geeko"). The frontend polls the API every couple of seconds and
renders an animated SVG character whose look reacts to the live state:

- **alive** (API reachable): idle bob animation, eyes moving, tongue flicking, periodic "JUL" hand
  sign, body color driven by live state.
- **sulking** (API unreachable): arms crossed, frown — the same visual is reused for any kind of
  outage (killed pod, network partition, whatever caused the frontend to lose the API).

## Architecture

```
┌─────────────┐      /api/*       ┌───────────┐      redis://      ┌────────────┐
│  frontend    │ ───(nginx proxy)─▶│ geeko-api │────────────────────▶│ geeko-redis│
│ (static +    │                   │ (FastAPI) │                     │ (state)    │
│  inline SVG) │                   └─────┬─────┘                     └────────────┘
└─────────────┘                          │ SAGE_URL (optional)
                                          ▼
                                   ┌─────────────┐
                                   │ geeko-sage  │  (legacy fortune service,
                                   │ (FastAPI)   │   can live on a separate VM)
                                   └─────────────┘
```

- **`frontend/`** — static HTML/CSS/JS, inline SVG character, nginx reverse-proxies `/api/` and
  `/healthz` to `geeko-api` server-side (so the browser only ever talks to one origin — no CORS,
  and it keeps working transparently behind a nested reverse-proxy path prefix, since all API calls
  are made with page-relative paths, never a leading `/`).
- **`geeko-api/`** — FastAPI service. A background loop ticks the simulated state (position, color,
  mood) into Redis every `TICK_SECONDS`. Exposes `/healthz`, `/api/geeko` (current state), and
  `/api/sage` (proxies a fortune from the legacy service, degrading gracefully to
  `{"available": false}` if it's unset or unreachable — this is intentional, not a bug: the legacy
  service is optional infrastructure, not a hard dependency).
- **`sage/`** — the "legacy" service: a tiny FastAPI app returning a fortune plus a `patched` flag.
  `patched` is simply whether a flag file (`GEEKO_SAGE_FLAG_PATH`, default
  `/etc/geeko-sage/patched`) exists — meant to be toggled by an external patch/config-management
  process, not by the app itself. Ships as a container (`Dockerfile`) for local dev and as a plain
  systemd unit + `install.sh` for running directly on a VM.
- **`helm/geeko/`** — the Helm chart used to deploy `frontend` + `geeko-api` + (optionally) a Redis
  dependency onto Kubernetes.

## Redis: an intentional supply-chain contrast

`values.yaml` has a `redis.source` toggle:

- `dockerhub` (default) — a raw, unpinned community image straight from Docker Hub. Deliberately the
  "before" state.
- `appco` — when set, the chart deploys **no Redis at all**; instead you install Redis as its own
  Helm release from the SUSE Application Collection (signed, SBOM'd, hardened) and point
  `api.redisUrl` at that service. This is the "after" state.

Same idea applies to the exact image tag used in `dockerhub` mode — swapping to an old/CVE-heavy tag
vs. an Alpine tag is a good way to show a vulnerability scanner (e.g. NeuVector) reporting a real
difference.

## Reaching a legacy service over Tailscale (optional)

`geeko-api` doesn't need `geeko-sage` to run — `api.sageUrl` is empty by default and the frontend
just shows the Sage banner as unavailable. If you do want to wire it up to a Sage instance running
somewhere the cluster can't otherwise reach (a VM on a separate network, say), the chart supports an
opt-in Tailscale sidecar:

```yaml
tailscale:
  enabled: true       # off by default — nothing below applies unless this is true
  secretName: geeko-tailscale-auth
```

This adds a `tailscale/tailscale` sidecar container to the `geeko-api` pod (sharing its network
namespace) and reads `SAGE_URL` + the Tailscale auth key from a Kubernetes Secret you create
yourself — **never commit real values for this**, they only ever live in a Secret created directly
in your cluster:

```
kubectl create secret generic geeko-tailscale-auth \
  --from-literal=authkey=tskey-auth-... \
  --from-literal=sage-url=http://100.x.y.z:9000 \
  -n <namespace>
```

## Running locally

```
docker compose up
```

Brings up all four services (`geeko-redis`, `geeko-api`, `geeko-sage`, `geeko-frontend`) wired
together, frontend on `http://localhost:8080`.

## Deploying with Helm

```
helm install geeko-app ./helm/geeko -n <namespace> --create-namespace
```

Key `values.yaml` knobs:

| Key | Default | Purpose |
|---|---|---|
| `image.repository` | `cyrilcuvier/geekoapp` | Docker Hub repo (one tag per component: `api-x.y.z`, `frontend-x.y.z`) |
| `api.redisUrl` | `redis://geeko-redis:6379/0` | Redis connection string |
| `api.sageUrl` | `""` | Sage service URL — leave empty if you don't have one |
| `redis.source` | `dockerhub` | `dockerhub` (bundled anti-pattern) or `appco` (bring your own, e.g. Application Collection) |
| `tailscale.enabled` | `false` | Opt-in sidecar to reach a Sage instance over Tailscale, see above |

Bump `Chart.yaml`'s `version` whenever chart content changes, and bump the relevant image tag
whenever an image's content changes — both are required for Kubernetes/Helm to actually pick up the
new content (`pullPolicy: IfNotPresent` won't re-pull an unchanged tag).
