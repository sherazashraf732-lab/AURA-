# 10 — GitHub, CI/CD, Deployment and Migration

## GitHub repository
- One canonical repository initially.
- Protect main branch where available.
- Use feature branches and pull requests for risky work.
- Include README, license decision, contribution/security docs, changelog and architecture docs.
- Add `.gitignore` for secrets, local DBs, uploads, caches, build outputs and virtual environments.
- Never commit `.env`, provider keys, production data or private user uploads.

## CI pipeline
On pull request and main:
1. Install pinned dependencies.
2. Run format/lint.
3. Run type checks.
4. Run backend unit tests.
5. Run frontend tests/build.
6. Run migration validation.
7. Run dependency and secret scans.
8. Run integration/E2E suite where infrastructure permits.
9. Build deployment artifacts.

Do not deploy if required checks fail.

## Hosting strategy candidates
- Frontend: Vercel or equivalent.
- FastAPI backend and worker: Render or another suitable Python host.
- PostgreSQL/auth/storage: Supabase or separately managed compatible services.
These are candidates, not guarantees. At implementation time verify current free-tier limits, sleep behavior, CPU/RAM, storage, bandwidth, build minutes, region availability and terms. Do not promise unlimited free hosting.

## Environment separation
- Local development.
- CI/test.
- Staging.
- Production.
Use separate credentials and databases. Never copy production secrets into local files or GitHub.

## Persistence
- Database backups.
- Object storage backups or versioning.
- Migration scripts.
- Restore instructions.
- Verify restore periodically.
- App filesystem is not permanent production storage unless host explicitly guarantees persistence.

## GitHub is not the application host
GitHub stores source code and runs CI/CD workflows. GitHub Pages is for static sites; it does not run the Python FastAPI backend. The frontend and backend need actual hosting.

## Migration to a new computer/server
Provide:
- Git clone instructions.
- Supported runtime versions.
- `.env.example`.
- Dockerfiles/Compose where useful.
- Lockfiles.
- Database migrations.
- Backup/restore scripts.
- Object storage migration steps.
- Smoke-test script.
- Deployment runbook.
Secrets must be supplied separately on the new machine. Never place secrets in the ZIP or repository.

## Desktop release
Only after web beta is stable:
- Package Tauri app.
- Verify Windows signing/distribution requirements.
- Use same backend API.
- Restrict local file permissions.
- Test update strategy and secure API communication.
