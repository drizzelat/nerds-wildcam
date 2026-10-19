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

## Endpoints

- `/` form + full log
- `/health` JSON health check (use for Traefik / k8s probes)

TLS is expected to terminate at the load balancer; `X-Forwarded-*` headers are trusted.
