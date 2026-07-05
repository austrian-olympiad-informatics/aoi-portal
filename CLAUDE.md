# CLAUDE.md

Guidance for working in this repo, the portal for the Austrian Olympiad in
Informatics (AOI).

## Overview

The portal handles registration, login (incl. OAuth/SSO), and contest
administration for the AOI, and provides single-sign-on into the CMS contest
system. It's a single-page app talking to a JSON API.

- **backend/** — Flask API (Python). Package `aoiportal`. Owns the portal
  database (users, contests, registrations, sessions).
- **frontend/** — Vue 2 single-page app (Bulma/Buefy), served separately and
  proxied to the backend under `/api`.
- **docker/** — nginx + configs for the Docker Compose dev stack.

Because the portal's dependencies are incompatible with CMS's, integration with
CMS goes through a thin bridge rather than importing CMS directly.

## CMS integration

CMS (Contest Management System) is a separate project, kept as a **sibling
checkout at `../cms`** (the AOI fork of cms-dev). The portal touches it two ways:

- **`backend/aoiportal/cmsmirror/`** — a read-only SQLAlchemy mirror of the CMS
  database. It re-declares the CMS tables so the portal can query contest data
  directly. It must match the schema of the CMS the portal connects to; when CMS
  models change, the mirror has to be updated to match.
- **RPC** to the CMS evaluation service for actions that mutate CMS state.

## Running it

See [DEVELOPMENT.md](DEVELOPMENT.md). In short: `docker compose up` builds the
whole stack (portal + CMS from `../cms`) and initializes the databases.

## Conventions

- **Python dependencies are managed with `uv`.**
- Backend and frontend source are bind-mounted into their containers, so changes
  reload without rebuilding; CMS code is baked into its image and needs a rebuild.
- The backend is intentionally decoupled from CMS internals — reach CMS through
  `cmsmirror` (reads) or the RPC bridge (writes), not by importing CMS.
- Keep the frontend/backend contract in JSON at `/api`; the frontend has no
  direct DB access.
- Match the style of the surrounding code; the backend and CMS mirror follow
  CMS's SQLAlchemy model conventions.
