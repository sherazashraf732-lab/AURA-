# AURA — Your AI Powerhouse

Private, proprietary source (all rights reserved). See `DECISIONS.md` (license decision L).

AURA is a multilingual AI workspace: chat with multiple free-tier model providers, projects, user-controlled memory, automatic continuation of long chats, and English / Urdu / Roman Urdu language matching. Further modules are being built phase by phase; `BUILD_STATUS.md` is the source of truth for what works today.

## Repository layout

| Path | What |
|---|---|
| `backend/` | FastAPI modular monolith (Python 3.12, SQLAlchemy 2, Alembic, PostgreSQL) |
| `apps/web/` | React 19 + TypeScript + Vite + Tailwind 4 web app |
| `docs/`, `specs/`, `configs/`, `templates/` | Approved specification package (unchanged) |
| `PHASE_0/`, `PHASE_1/` | Historical research and decision reports |
| `scripts/` | Developer scripts (local PostgreSQL) |

## Run locally on Windows (8 GB RAM friendly)

Prerequisites: Git, Node 24, `uv` (installs Python 3.12 for the project). No Docker, WSL or system PostgreSQL needed.

1. **Database** — project-local PostgreSQL 18 binaries live in `.local/pgsql` (git-ignored). Download the official EDB "Windows x86-64 binaries" zip for PostgreSQL 18 and extract it so that `.local/pgsql/bin/pg_ctl.exe` exists. Then:

   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\dev-db.ps1 start
   ```

   This listens only on `127.0.0.1:5433` and creates databases `aura` and `aura_test`.

2. **Backend**

   ```powershell
   cd backend
   copy .env.example .env   # then set SECRET_KEY; provider keys are optional
   uv sync
   uv run alembic upgrade head
   uv run uvicorn app.main:app --port 8000
   ```

3. **Web**

   ```powershell
   cd apps/web
   npm install
   npm run dev
   ```

   Open http://localhost:5173. In development, verification and reset emails are written to the `outbox_emails` table instead of being sent.

## Tests

```powershell
cd backend; uv run pytest; uv run ruff check .; uv run mypy app
cd apps/web; npm test; npm run lint; npm run typecheck; npm run build
```

## Safety defaults

- Paid AI providers are disabled (`ALLOW_PAID_PROVIDER_USAGE=false`); quota exhaustion never switches to a paid provider.
- External providers require each user's explicit consent; the offline demo model never sends data anywhere.
- Secrets live only in `backend/.env` (git-ignored) or the hosting provider's secret manager.
