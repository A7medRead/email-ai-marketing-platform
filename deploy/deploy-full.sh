#!/usr/bin/env bash
# Full deployment: backend, frontend, Compose config and database migrations.
# For frontend-only changes use deploy/deploy-frontend.sh instead.
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
ssh_identity="${HOME}/.ssh/madar_vps"
remote_host="deploy@159.195.115.229"
remote_root="/opt/mailpilot"
ssh_options=(-i "${ssh_identity}" -o IdentitiesOnly=yes -o BatchMode=yes -o StrictHostKeyChecking=yes)

if [[ ! -r "${ssh_identity}" ]]; then
    echo "Missing deployment SSH identity: ${ssh_identity}" >&2
    exit 1
fi

# Only build inputs are sent. .env, emails.db, uploads and backups stay on the VPS.
COPYFILE_DISABLE=1 tar --format=ustar -cf - \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='frontend/.env*' \
    --exclude='frontend/.npmrc' \
    --exclude='__pycache__' \
    --exclude='._*' \
    -C "${repo_root}" \
    app alembic alembic.ini requirements.txt Dockerfile Dockerfile.frontend compose.yaml \
    frontend deploy DEPLOYMENT.md \
    | ssh "${ssh_options[@]}" "${remote_host}" \
        "tar -xf - -C '${remote_root}' && \
         find '${remote_root}' -maxdepth 3 -type f -name '._*' -delete && \
         cd '${remote_root}' && \
         docker compose up -d --build && \
         docker compose ps && \
         docker compose exec -T api alembic current && \
         for url in http://127.0.0.1:8081/ http://127.0.0.1:8081/api/; do \
             ok=0; \
             for attempt in \$(seq 1 30); do \
                 if curl -fsS -o /dev/null \"\$url\"; then ok=1; break; fi; \
                 sleep 2; \
             done; \
             [ \$ok -eq 1 ] || { echo \"Health check failed: \$url\" >&2; exit 1; }; \
         done && \
         echo 'Full deployment health checks passed.'"
