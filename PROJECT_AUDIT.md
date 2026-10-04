# Project audit and remediation tracker

Last reviewed: 2026-10-04

Status: `OPEN`, `IN PROGRESS`, `RESOLVED`, or `BLOCKED`.

## Findings

| ID | Priority | Finding | Status | Notes |
| --- | --- | --- | --- | --- |
| A1 | High | The deployed account uses a reserved `.test` address. `UserResponse` validates it as a deliverable email, so `/users/me` returns HTTP 500. | RESOLVED | `UserResponse.email` now serializes stored values as text; public registration still uses `EmailStr`. Verified authenticated `/users/me` returns HTTP 200 on the VPS. |
| A2 | Critical | Password reset returns the raw reset token to the caller, reveals whether an email exists, has no mail delivery, and its reset screen is behind authentication. | BLOCKED | Generic responses, SMTP delivery, URL token handling, and public reset route are deployed. Checked VPS environment: SMTP settings are all absent. Configure `SMTP_HOST`, `SMTP_FROM_EMAIL` and, if needed, `SMTP_USERNAME`/`SMTP_PASSWORD` to enable delivery. |
| A3 | High | Public unsubscribe uses a predictable contact ID and assigns a status value not present in `ContactStatus`. | RESOLVED | Unsubscribe uses a signed purpose-bound token, stores `ContactStatus.UNSUBSCRIBED`, adds a link to campaign mail, and sender skips opted-out contacts. Deployed. |
| A4 | High | The public app is served over HTTP on port 8081 without TLS. | BLOCKED | User chose IP access and no domain. A browser-trusted TLS certificate needs a domain or another trusted certificate setup. |
| A5 | High | Frontend lint fails and dependency installation reported 32 advisories, including 6 high. | RESOLVED | Lint passes with no warnings; compatible Tiptap updates plus `npm audit fix` removed the reported advisories (`0 vulnerabilities`). The VPS production image built with the updated lockfile. |
| A6 | Medium | Contact export uses the list endpoint's default page size and exports at most 10 contacts. | RESOLVED | Added an unpaginated repository query scoped to the current user. Deployed. |
| A7 | High | Avatar and CSV uploads have no application-level size/type validation. | RESOLVED | Avatar uploads are capped at 5 MB and re-encoded from JPEG/PNG/WebP; CSV imports are capped at 10 MB and validate UTF-8 plus the required email header. Deployed. |
| A8 | High | Production startup calls `create_all()` rather than applying Alembic migrations; no MailPilot database backup job is configured. | RESOLVED | Compose backed up the SQLite DB, ran Alembic before app services, and started a daily verified backup worker with 14-copy retention. Backup files are present on the VPS. Restore steps are documented. |
| A9 | Medium | No automated test suite was found; lint currently fails. | IN PROGRESS | Lint is clean. No automated application test suite exists yet; targeted coverage remains. |
| A10 | Medium | Campaign scheduling runs inside the API process. Multiple API replicas would run duplicate schedulers and could send duplicate campaigns. | RESOLVED | Moved scheduling into a dedicated Compose worker protected by a shared Docker-volume file lock. VPS logs confirm the lock was acquired by the single scheduler worker. |
| A11 | High | The public click-tracking route accepts an arbitrary destination URL and can be used as an open redirect. | RESOLVED | Click destinations are now carried in a purpose-bound signed token and limited to HTTP(S). Deployed. |
| A12 | Medium | Backend and frontend files were organized by technical layer or flat page folders, with legacy snapshots and fixtures mixed into runtime source. | RESOLVED | Reorganized both apps by product feature, centralized ORM model registration for API and worker processes, moved historical files/fixtures to `archive/`, and added architecture/onboarding docs. Deployed to the VPS; API/web/scheduler/backup are running, HTTP checks return 200, and Alembic is at head. |

## Verification snapshot

- Deployed frontend and API root responded with HTTP 200 at `http://159.195.115.229:8081` after the feature reorganization.
- API, web, scheduler, and backup services are running on the VPS; the scheduler acquired its lock and started its job. Alembic is at `436cdefb599b (head)`.
- Frontend production build succeeded; the bundle is about 1.26 MB minified.
- `npm run lint` reported 16 errors and 7 warnings in active source, plus 5 errors in backup files.
- Local SQLite columns match the current ORM models; Alembic currently has one head.
- No automated test files were found.

## Change log

- 2026-10-04: Created this tracker from the project and deployed-service review. Remediation has not yet been verified.
- 2026-10-04: Fixed A1, A3 and A6 in source; implemented the secure password-recovery flow for A2, pending SMTP configuration. `python -m compileall -q app` and frontend production build pass. Frontend lint still reports 21 errors and 7 warnings (including 5 errors in backup files). Changes have not yet been deployed or verified against the VPS.
- 2026-10-04: Added 5 MB decoded-image validation/normalization for avatars and 10 MB UTF-8/header validation for CSV imports (A7); added signed tracking destinations (A11). A7/A11 are resolved in code and pending deployment. TLS remains blocked by the current IP-only/no-domain setup (A4).
- 2026-10-04: Fixed frontend lint, upgraded compatible frontend packages, and cleared npm advisories (A5). Removed API `create_all()`/embedded scheduler; Compose now runs a pre-migration backup + Alembic job, a single lock-protected scheduler worker, and a daily verified SQLite backup worker with 14-copy retention (A8/A10). Added deployment and recovery instructions. `npm run lint`, `npm run build`, Python compile, Compose configuration, and a SQLite backup smoke check pass. No code changes have been deployed to the VPS yet.
- 2026-10-04: Deployed the fixes to `/opt/mailpilot`. Alembic completed after a pre-migration backup; API, web, scheduler, and backup services are running. Verified public frontend/API return HTTP 200, authenticated `/users/me` returns HTTP 200, and the daily backup worker created integrity-checked backups on the VPS. A first authenticated ORM check used a standalone script that had not imported the app's model registry; the actual HTTP route check after app imports returned 200.
- 2026-10-04: Reorganized backend and frontend source by feature; added explicit `app/features/model_registry.py`; archived legacy copies and fixtures; added root onboarding and architecture docs. Initial deployment exposed that the standalone scheduler process also needs the ORM registry imported. Added that import in `app/workers/campaign_scheduler.py`, verified local ORM configuration and frontend lint, rebuilt on the VPS, and confirmed scheduler startup plus HTTP 200 for web/API. Archive of prior source is retained on the VPS; database, uploads, environment, and backups were preserved.
