# Development setup

This describes the **Docker Compose** dev environment, which brings up the whole
stack (portal + CMS) with one command and auto-initializes both databases. For
the Nix-based alternative see the `devenv.sh` section in the [README](README.md).

## Architecture

```
              nginx :8080
              /          \
        /api /             \ /
   backend (Flask)      frontend (Vue 2 dev server)
      |        \
   db (portal)  \--- cmsmirror (read-only) ---> cmsdb
                 \--- evaluation RPC --------> cms-evaluation-service
                                                      |
   cms-admin-web-server :8889   cms-scoring-service   cms-worker-0
```

- **backend** — Flask API. Talks to its own `db` (portal users/contests) and,
  through `cmsmirror` (a read-only SQLAlchemy mirror of the CMS schema), to
  `cmsdb`. Submissions etc. are driven via RPC to the CMS services.
- **CMS** — built from a **sibling checkout** at `../cms` (the Austrian fork of
  cms-dev). Its `isolate` sandbox is a git submodule, patched to build on arm64
  (Apple Silicon).

## Prerequisites

- Docker (Desktop on macOS, or Docker Engine + Compose v2 on Linux).
- The CMS repo checked out **next to** this one, with submodules:

  ```bash
  git clone --recurse-submodules <cms-repo-url> ../cms   # ends up at ../cms
  # or, if already cloned:
  git -C ../cms submodule update --init
  ```

  The `docker-compose.yml` builds the CMS images from `../cms`, so the directory
  layout must be:

  ```
  <parent>/
    aoi-portal/   <- this repo
    cms/          <- sibling CMS checkout (with isolate submodule)
  ```

## Quick start

```bash
docker compose up -d          # build + start everything
docker compose logs -f backend frontend   # watch startup (first build is slow)
```

On first `up`, the stack automatically:
- waits for both Postgres DBs (healthchecks),
- creates the **portal** schema and a default admin,
- creates the **CMS** schema (`cms-initdb`, idempotent),
- starts the CMS services and the frontend dev server.

The frontend's first `npm install && npm run serve` takes a couple of minutes —
wait for `App running at:` in its logs before the portal loads.

### Access points

| URL | What | Login |
|-----|------|-------|
| http://localhost:8080/ | Portal (frontend + `/api`) | `t.rainer@example.org` / `password1` |
| http://localhost:8889/ | CMS AdminWebServer | needs a CMS admin — see below |

The portal admin is created automatically. The **CMS** admin web server has its
own accounts; create one once:

```bash
docker compose exec cms-console cmsAddAdmin <username>
# it prints a generated password (or pass -p <password>)
```

## Common operations

```bash
# Rebuild after changing CMS code in ../cms (code is baked into the image):
docker compose build cms-console cms-admin-web-server cms-evaluation-service \
                     cms-scoring-service cms-worker-0 && docker compose up -d

# Backend/frontend code is bind-mounted (./backend, ./frontend) — no rebuild
# needed; the backend reloads and the frontend recompiles on change.

# A shell in the CMS environment (cmsImportContest, cmsAddAdmin, etc.):
docker compose exec cms-console bash

# Reset a database from scratch (destroys local dev data):
docker compose down
rm -rf ./data/db        # portal DB   -> re-created + admin re-added on next up
rm -rf ./data/cmsdb     # CMS DB      -> re-created by cms-initdb on next up
docker compose up -d
```

Postgres data lives in `./data/db` (portal) and `./data/cmsdb` (CMS); both are
gitignored.

## Configuration

- Portal backend config: `docker/config.yaml` (mounted at `/config.yaml`).
- CMS config: `docker/cms.docker.toml` (TOML — upstream cms-dev dropped the old
  JSON `cms.conf`). It's mounted at `/config/cms.toml` and selected via the
  `CMS_CONFIG` env var. Only the CMS services we actually run are given real
  hostnames in `[services]`; the rest point at `localhost` and are simply
  unreachable (harmless warnings).

## The CMS dependency

`../cms` tracks the Austrian fork of cms-dev. If the CMS image fails to build:

- Ensure the `isolate` submodule is checked out (`git -C ../cms submodule update
  --init`). It's built from source (not `apt`) so the sandbox works on arm64.
- On Apple Silicon, isolate compiles for arm64 but the sandbox only *runs*
  meaningfully under a Linux host with cgroup v2 — for portal development you
  usually only need the CMS services to start and be reachable, which they do.
