# Deployment (not yet performed — needs owner approval)

AURA is a FastAPI API + worker threads and a static React app. Recommended free-tier layout (verify limits before use):

| Part | Candidate | Notes |
|---|---|---|
| Web app (static `apps/web/dist`) | Vercel Hobby or Cloudflare Pages | Vercel Hobby is non-commercial only |
| API (`backend/`) | Any Python host with one always-on process | Render free was unverifiable; check sleep behaviour |
| PostgreSQL 16+ | Neon free (1 GB, pgvector) or Supabase free (pauses after 7 days idle) | Run `alembic upgrade head` on deploy |
| Email | Resend free (100/day) | Needs a verified sending domain |
| Errors | Sentry Developer (free) | Set `SENTRY_DSN`; no request bodies or PII are sent |

## Steps
1. Create the database; set `DATABASE_URL`, `SECRET_KEY` (64+ random chars), `APP_ENV=production`, `APP_URL`, `CORS_ORIGINS`, `RESEND_API_KEY`, `MAIL_FROM`, `BOOTSTRAP_ADMIN_EMAIL`, provider keys — all in the host's secret manager, never in Git.
2. `cd backend && uv sync --no-dev && uv run alembic upgrade head`
3. Start: `uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT` (one process: rate limits and scheduler are in-process).
4. Build the web app (`npm ci && npm run build`) and serve `dist/` with `/api` proxied to the API on the same domain (cookies are same-site).
5. Sign up with `BOOTSTRAP_ADMIN_EMAIL`, verify, and check `/app/admin`.
6. Smoke test: `scripts/smoke_e2e.py` with `AURA_BASE=https://your-domain`.

## Backups
`scripts/backup-db.ps1 backup` (pg_dump custom format) and `restore -File <dump> -Db <new_db>`; restoring over the live DB is refused. Verified locally on 2026-11-20 (row counts and migration version matched). In production, schedule daily dumps, encrypt them, keep 30 days off-site, and test a restore monthly.

## Rollback
Redeploy the previous Git commit; run `alembic downgrade -1` only if the new migration is the cause and data loss has been ruled out.
