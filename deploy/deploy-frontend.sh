#!/usr/bin/env bash
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

COPYFILE_DISABLE=1 tar --format=ustar -cf - \
    --exclude='frontend/node_modules' \
    --exclude='frontend/dist' \
    --exclude='frontend/.env*' \
    --exclude='frontend/.npmrc' \
    --exclude='frontend/._*' \
    -C "${repo_root}" \
    frontend Dockerfile.frontend deploy/nginx.conf deploy/deploy-frontend.sh DEPLOYMENT.md \
    | ssh "${ssh_options[@]}" "${remote_host}" \
        "tar -xf - -C '${remote_root}' && \
         find '${remote_root}/frontend' -type f -name '._*' -delete && \
         cd '${remote_root}' && \
         docker compose build web && \
         docker compose up -d --no-deps web && \
         docker compose ps web api && \
         curl -fsS -o /dev/null http://127.0.0.1:8081/ && \
         curl -fsS -o /dev/null http://127.0.0.1:8081/api/ && \
         echo 'Frontend and API health checks passed.'"
