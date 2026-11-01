# GMS Backend — Setup & Run Guide

## Prerequisites

| Tool | Verified version | Why |
| :--- | :--- | :--- |
| **Docker + Docker Compose** | Docker 27.4, Compose v2.31 (Docker Desktop) | Runs the whole stack. |
| **Docker Desktop memory** | **≥ 10–12 GB allocated** | The full fleet is 9 containers; with less, MySQL gets OOM-killed (exit 137). |
| **Python 3.11** | 3.11.13 | Only needed for the *without-Docker* path (§3). The images use `python:3.11-slim`. |
| **git** | any | To clone. |

> All commands run from the `gms_be/` directory (the repo root that contains `docker-compose.yml`).

---

> **Which section do I need?** You have two options:
>
> - **Run only the services you need (§1)** — the recommended starting point. Naming a service
>   auto-starts just the infra it needs (MySQL + Redis), so you can get your hands on one service
>   fast and light.
> - **Run everything at once (§2)** — the full 9-container fleet. This needs **more RAM
>   (≥ 10–12 GB allocated to Docker)** and on smaller / lower-spec machines it may not work as
>   expected (MySQL can get OOM-killed). Only reach for §2 if you actually need the whole stack up.
>
> So start with §1 and bring up just what you need. If you genuinely want everything running,
> head to §2.

---

## Section 1 — Run a service independently (Docker, recommended)

You don't have to run all 9 containers. Each service `depends_on` `db` and `broker`, so **naming a
service auto-starts the infra** and waits until MySQL + Redis are healthy before it boots. Run
`./build.sh` once first so the images exist:

```bash
cd gms_be
cp .env.example .env       # fresh-clone step; a ready-to-use .env ships in the repo
./build.sh                 # builds the shared gms-base image, then all service images
```

```bash
# Shared infra (starts automatically with any service below, or bring it up alone):
docker compose up -d db broker
```

**Start any single service** — infra auto-starts if not already up:

```bash
docker compose up -d auth-admin-service       # :5004  login / auth / admin
docker compose up -d members-service          # :5005  members, memberships, bookings
docker compose up -d plans-classes-service    # :5006  plans, classes, schedules
docker compose up -d reports-service          # :5008  reports
docker compose up -d frontend                 # :8080  web console (needs the API services above)
docker compose up -d email-worker             # consumes the :emails queue
docker compose up -d batch-worker             # consumes the :batch-queue queue
docker compose up -d scheduler                # Celery Beat (skeleton — see gotcha 6)
```

Combine any set — shared infra starts once, not per service:

```bash
docker compose up -d auth-admin-service members-service
```

**Follow logs** (drop `-f` for a one-shot dump; add `--tail=100` to limit):

```bash
docker compose logs -f auth-admin-service
docker compose logs -f members-service
docker compose logs -f plans-classes-service
docker compose logs -f reports-service
docker compose logs -f email-worker
docker compose logs -f batch-worker
docker compose logs -f scheduler
docker compose logs -f db broker              # infra logs (pass multiple names)
```

**Stop / restart one service** — the rest of the stack is untouched:

```bash
docker compose stop reports-service           # stop just this one
docker compose up -d reports-service          # start it again
docker compose restart reports-service        # stop + start in one step
docker compose ps                             # what's currently up
```

**Quick reference:**

| Service | Start | Logs | Stop |
| :--- | :--- | :--- | :--- |
| auth-admin (:5004) | `docker compose up -d auth-admin-service` | `docker compose logs -f auth-admin-service` | `docker compose stop auth-admin-service` |
| members (:5005) | `docker compose up -d members-service` | `docker compose logs -f members-service` | `docker compose stop members-service` |
| plans-classes (:5006) | `docker compose up -d plans-classes-service` | `docker compose logs -f plans-classes-service` | `docker compose stop plans-classes-service` |
| reports (:5008) | `docker compose up -d reports-service` | `docker compose logs -f reports-service` | `docker compose stop reports-service` |
| frontend (:8080) | `docker compose up -d frontend` | `docker compose logs -f frontend` | `docker compose stop frontend` |
| email-worker | `docker compose up -d email-worker` | `docker compose logs -f email-worker` | `docker compose stop email-worker` |
| batch-worker | `docker compose up -d batch-worker` | `docker compose logs -f batch-worker` | `docker compose stop batch-worker` |
| scheduler | `docker compose up -d scheduler` | `docker compose logs -f scheduler` | `docker compose stop scheduler` |
| db / broker (infra) | `docker compose up -d db broker` | `docker compose logs -f db broker` | `docker compose stop db broker` |

**Light mode** (a useful middle ground — the 4 APIs + infra, but skip workers + scheduler to save RAM):

```bash
docker compose up -d db broker auth-admin-service members-service plans-classes-service reports-service
```

**Verify** a service you started (returns `HTTP 200`):

```bash
curl http://localhost:5004/api/v1.1/auth/health      # auth-admin
curl http://localhost:5006/api/v1/pp/health          # plans-classes
curl http://localhost:5008/api/v1/reports/health     # reports
open  http://localhost:5005/docs                     # members — Swagger UI
```

> Workers only do work when an API service publishes a task — bring up the relevant API service
> alongside `email-worker` / `batch-worker` to exercise them.

---

## Section 2 — Run everything with Docker

Only reach for this if you actually need the whole stack up **and** your machine has the RAM for it
(≥ 10–12 GB allocated to Docker). On smaller machines, prefer §1.

```bash
cd gms_be

# 1. Environment file (a ready-to-use .env ships in the repo; this is the fresh-clone step)
cp .env.example .env

# 2. Build the shared base image first, then all service images
#    (every service is FROM gms-base; compose can't order image builds, so build.sh does)
./build.sh

# 3. Start the fleet: MySQL + Redis + 4 API services + 2 workers + scheduler
docker compose up -d
```

Compose waits for MySQL and Redis to be **healthy** before starting the services (via
`depends_on` healthchecks). On first start, MySQL auto-loads `gmsshared/db/init.sql` — the
full schema plus a sample seed (a gym, location, staff, 40 members, 28 plans, 60 memberships).

**Verify it's up** (all four return `HTTP 200`):

```bash
curl http://localhost:5004/api/v1.1/auth/health      # {"status":"SUCCESS","message":"Auth health is good","data":{}}
curl http://localhost:5006/api/v1/pp/health          # {"status":"SUCCESS","message":"Plans health is good","data":{}}
curl http://localhost:5008/api/v1/reports/health     # {"status":"SUCCESS","message":"Reports health is good","data":{}}
open  http://localhost:5005/docs                     # members — Swagger UI
```

Every API service also serves interactive docs at **`/docs`** and the raw spec at **`/openapi.json`**.

**Verify end-to-end** with a real login (seed user — returns a JWT):

```bash
curl -X POST http://localhost:5004/api/v1.1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"owner@demo.gym","password":"Test@1234"}'
# -> {"status":"SUCCESS","message":"owner@demo.gym logged in","data":{"access_token":"...","refresh_token":"..."}}
```

**Login for every seeded user:** `owner@demo.gym` / `Test@1234`

**Ports & endpoints (verified):**

| Service | Host port | Health / entry |
| :--- | :--- | :--- |
| auth-admin | 5004 | `/api/v1.1/auth/health` |
| members | 5005 | `/docs` (Swagger) |
| plans-classes | 5006 | `/api/v1/pp/health` |
| reports | 5008 | `/api/v1/reports/health` |
| MySQL | **3307** → 3306 | user `gms` / pass `gms`, db `gms` (root pass `gms`) |
| Redis | *internal only* | services reach it as `broker:6379` on the compose network |

**Tear down:**

```bash
docker compose down        # stop & remove containers (keeps the DB volume)
docker compose down -v      # also wipe the MySQL data volume (fresh seed next time)
```

---

## Section 3 — Run a service without Docker (native)

The Python service runs on your host, but it still needs **MySQL + Redis** reachable. The
simplest verified setup is to run just those two in Docker and the service natively.

```bash
# 1. Infra only (MySQL published on host 3307)
docker compose up -d db broker

# Redis has no host port by default. Give the native service a Redis on localhost:6379 — either:
docker run -d --name gms-redis -p 6379:6379 redis:7-alpine        # a standalone one, or
# add   ports: ["6379:6379"]   under the `broker` service in docker-compose.yml
```

```bash
# 2. Python env (must be 3.11) + install the shared lib FIRST, then the service
cd gms_be
python3.11 -m venv venv
source venv/bin/activate
pip install -e ./gmsshared            # shared library — install before any service
pip install -e ./auth-admin-service   # the service you want to run
```

```bash
# 3. Native env file — point at the HOST, not the compose hostnames
cp .env.example .env.native
# then edit .env.native so these three read:
#   SQLALCHEMY_DATABASE_URI=mysql+mysqlconnector://gms:gms@127.0.0.1:3307/gms
#   BROKER_URI=redis://localhost:6379/0
#   BACKEND_URI=redis://localhost:6379/1
```

```bash
# 4. Run it EXACTLY like the Dockerfile does: from the repo root, PYTHONPATH=.
set -a; . .env.native; set +a
PYTHONPATH=. gunicorn -k uvicorn.workers.UvicornWorker \
  -c auth-admin-service/gunicorn.conf.py \
  "auth-admin-service.src:create_app()"
```

**Verify (returns `HTTP 200`):**

```bash
curl http://localhost:5004/api/v1.1/auth/health
```

> **The one gotcha that will bite you:** run from the **repo root** with **`PYTHONPATH=.`**.
> `gmsshared` is imported as a namespace *directory* on the path (`gmsshared.src.config`), so if
> you run from inside `auth-admin-service/`, it fails with
> `ModuleNotFoundError: No module named 'gmsshared'`.

**Other services natively** — same pattern, swap the app spec, config path, and port:

| Service | App spec | Config | Port |
| :--- | :--- | :--- | :--- |
| members | `members-service.src:create_app()` | `members-service/gunicorn.conf.py` | 5005 |
| plans-classes | `plans-classes-service.src:create_app()` | `plans-classes-service/gunicorn.conf.py` | 5006 |
| reports | `reports-service.src:create_app()` | `reports-service/gunicorn.conf.py` | 5008 |

**Workers natively** (no gunicorn — they're plain Celery processes):

```bash
PYTHONPATH=. python email-worker/run.py
PYTHONPATH=. python batch-worker/run.py
```

---

## Known gotchas (all real)

1. **Docker memory ≥ 10–12 GB** to run everything (§2), or MySQL is OOM-killed (exit 137). On smaller machines, run only what you need (§1).
2. **MySQL is on host port 3307**, not 3306 — deliberately, to avoid clashing with a local MySQL.
3. **Redis is internal by default** (no host port); publish it or run a standalone one for the native path (§3).
4. **Native: repo root + `PYTHONPATH=.`** — `gmsshared` resolves as a namespace directory, not the installed package.
5. **`cryptography` is pinned to `44.0.1`** — `>=47` ships Rust wheels that `SIGILL` on some Apple-Silicon Docker setups.
6. **The `scheduler` service is a skeleton** — it starts, but no cron jobs are wired up yet.
