# MailPilot

MailPilot is an AI-assisted email marketing application with campaign, contact,
sender-account, template, and analytics features.

## Start locally

1. Copy `.env.example` to `.env` and set the required application secrets.
2. Start the services with `docker compose up -d --build`.
3. Open `http://localhost:8081`. The API docs are available at
   `http://localhost:8081/api/docs`; the API container stays private to the
   Docker network.

For frontend-only development, run `npm ci && npm run dev` from `frontend/`.
The backend uses Python 3.12; install `requirements.txt` in a virtual environment
before running `uvicorn app.main:app --reload`.

## Project map

- `app/features/`: backend capabilities. Each feature owns its API, business
  service, repository, schemas, and models where needed.
- `app/core/`: shared authentication, security, configuration, and dependencies.
- `app/infrastructure/`: database/session setup and external integrations.
- `app/workers/`: background scheduler processes.
- `app/ops/`: backup utilities and operational jobs.
- `frontend/src/app/`: route composition and global app styles.
- `frontend/src/features/`: feature pages and feature-specific components.
- `frontend/src/shared/`: reusable UI, API client, and shared assets.
- `frontend/src/layouts/`: authenticated layout and route protection.
- `alembic/`: database migrations. Do not add schema changes to API startup.
- `archive/`: preserved legacy snapshots and sample files; not runtime code.

Read [ARCHITECTURE.md](ARCHITECTURE.md) before adding a feature and
[DEPLOYMENT.md](DEPLOYMENT.md) for VPS operations and database recovery.
