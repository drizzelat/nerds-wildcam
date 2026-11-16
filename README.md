# NERDS uc Wildcam Log

Tiny Flask app: log which animal was visible in which live stream, and when. Course vehicle for TU Wien 193.172 (Proxmox / Docker / Podman / Kubernetes / OpenShift / OpenStack).

## Run locally

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:8000, SQLite file by default
```

## Database

Set `DATABASE_URL` to use the dedicated DB server:

```bash
export DATABASE_URL='postgresql+psycopg2://user:pw@dbhost:5432/wildcam'
# or mysql+pymysql://user:pw@dbhost:3306/wildcam
```

## Docker

```bash
docker build -t wildcam .
docker run -p 8000:8000 -e DATABASE_URL=... wildcam
```

## Task 2: two apps (land & air / sea)

The repo root is the combined app from task 1 (Docker workers build it from here, left unchanged).
For task 2 it is split into two self-contained apps, each with its own code, template, `Containerfile` and DB table:

| Dir | App | Table | Extra field |
|-----|-----|-------|-------------|
| `land-air/` | land & air animals | `land_air_sighting` | kind (land/air) |
| `sea/` | sea animals | `sea_sighting` | depth (m) |

Both use the same `DATABASE_URL` (same DB server and database, separate tables) and listen on port 8000 in the container.

```bash
podman build -t wildcam-land-air land-air/
podman build -t wildcam-sea sea/
# or straight from GitHub:
podman build -t wildcam-sea https://github.com/drizzelat/nerds-wildcam.git#main:sea
podman run -d --name wildcam-land-air -p 8001:8000 --env-file /etc/wildcam.env wildcam-land-air
podman run -d --name wildcam-sea      -p 8002:8000 --env-file /etc/wildcam.env wildcam-sea
```

Behind Traefik both apps are served on one hostname under a path prefix (`/land-air/`, `/sea/`) with a `StripPrefix` middleware.
Traefik then sends `X-Forwarded-Prefix`, which the apps use for their links and redirects.
Optional `PEER_URL` env var (e.g. `/sea/`) adds a footer link to the other app.

## Endpoints

- `/` form + full log
- `/health` JSON health check (use for Traefik / k8s probes)

TLS is expected to terminate at the load balancer; `X-Forwarded-*` headers are trusted.
