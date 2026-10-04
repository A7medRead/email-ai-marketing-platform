# Deployment operations

## Deploying frontend updates to the VPS

The production VPS is `159.195.115.229`; SSH uses account `deploy`, identity
`~/.ssh/madar_vps`, and project directory `/opt/mailpilot`. Keep the private key
local and make sure the server host key is already in `~/.ssh/known_hosts`.

From the repository root, run:

```sh
bash deploy/deploy-frontend.sh
```

The script transfers only the frontend build inputs, `Dockerfile.frontend`, and
`deploy/nginx.conf`. It excludes local environment files, npm credentials,
installed dependencies, and local build output. On the VPS it rebuilds and
recreates only the `web` service, then checks the web and API endpoints. It does
not run database migrations or restart the API, scheduler, or backup worker.

For a backend or Compose change, review the full deployment impact first. The
general `docker compose up -d --build` command below also runs the migration
service and should not be used for frontend-only updates.

The API no longer creates database tables at startup. `docker compose up -d --build`
runs the `migrate` service first: it makes a verified SQLite backup, then applies
Alembic migrations before starting the API, scheduler, and backup worker.

The backup worker writes a verified database snapshot to `./backups` every 24 hours
and retains the newest 14. Before restoring, stop the API, scheduler, and backup
services. Copy a selected `emails-*.sqlite3` file over `emails.db` with `sudo cp`
(backup files are root-readable only), then start the stack again. Keep a separate
copy of `./backups` off the VPS for disaster recovery.

Only one campaign scheduler should be active at a time. The scheduler service holds
a shared Docker volume lock for its lifetime, so additional replicas wait for the
lock instead of sending campaigns concurrently.

Password recovery requires `SMTP_HOST`, `SMTP_FROM_EMAIL`, and (when the mail host
requires authentication) `SMTP_USERNAME` and `SMTP_PASSWORD`. Set `FRONTEND_URL` to
the public app URL so reset links return to the right host. Keep these values in the
untracked `.env` file and restart the API after changing them.
