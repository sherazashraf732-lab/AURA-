# PHASE 0 — Implementation Roadmap

- **Date:** 2026-11-20
- **Basis:** The approved 18-phase plan in `docs/11_PHASED_EXECUTION_PLAN.md` is kept as is. This roadmap adds, per phase, what must be installed, which shortlisted components apply, the exit gate, and the owner decisions that block it. Effort figures are rough (INFERRED) for one developer working with Claude Code on this laptop; they are not commitments.

## Release grouping (from `01_PRODUCT_BLUEPRINT.md`)

| Release | Phases |
|---|---|
| A — Foundation + secure public web beta | 1–7, 14–15 (a beta with chat, memory, workspaces) |
| B — Core intelligence and creation | 8–11 |
| C — Development and automation | 12 |
| D — Advanced file intelligence | 13 |
| E — Desktop client | 16 |

Note (INFERRED): the numbered plan places hardening (14) and public beta (15) after all modules. A smaller, earlier beta after Phase 7 (Release A) would get tester feedback sooner. This is an owner decision; the default remains the approved order.

## Phase table

| Phase | Goal | Installs needed (owner approval) | Components from shortlist | Exit gate | Blocking owner decisions | Rough effort |
|---|---|---|---|---|---|---|
| 1 | Open-source discovery deepening, ADRs | None (research only) | All shortlisted; scorecards | `OPEN_SOURCE_REGISTER.md`, ADRs for orchestration, provider layer, auth, queue, search, PDF writer, charts | AURA license; resolve conflicts C1–C6 | 2–4 days |
| 2 | Repository foundation | `gh` (optional), pnpm via corepack (optional), Python 3.12 venv via uv | ruff, mypy, ESLint, Vitest, pytest, GitHub Actions | Clean lint/type/test on empty app; CI green; no secrets | Repo name, public/private, project folder location | 1–2 days |
| 3 | Design system + animated shell | npm deps only | React, Vite, Tailwind, shadcn/ui, Motion, (GSAP), Three.js lazy, TanStack Query, React Router | All shell screens navigable; reduced-motion and Full/Reduced/Off work; a11y checks | GSAP license acceptance | 1–2 weeks |
| 4 | Backend + PostgreSQL | **PostgreSQL server** (native) | FastAPI, SQLAlchemy, Alembic, psycopg, pydantic-settings | Health endpoint; migrations up/down on test DB; structured errors | Native vs. hosted dev DB | 3–5 days |
| 5 | Auth + workspaces | Email provider account (test mode) | Auth option A or C; argon2-cffi; slowapi | Signup→verify→login→reset E2E; IDOR tests pass | Auth option, email provider | 1–2 weeks |
| 6 | Model router + central chat | Provider API keys (free tiers) | LiteLLM core behind adapter; mock provider; assistant-ui; SSE | Streaming chat; quotas; no paid fallback test | Which free providers; verified quotas | 1–2 weeks |
| 7 | Memory + continuation + language | — | lingua; Roman Urdu layer; own memory tables | Memory CRUD UI; continuation E2E; language tests incl. Roman Urdu and mixed | Thresholds, retention | 1–2 weeks |
| 8 | Research + agents + Control Room | — | LangGraph, trafilatura, search adapter, procrastinate | Cited report from fixtures; cancel/checkpoint tests; SSRF tests | Search provider | 2–3 weeks |
| 9 | Fact Checker + Knowledge Base | — | Postgres FTS / bm25s; pypdf; later pgvector | Ingestion + cited retrieval; isolation tests | — | 1–2 weeks |
| 10 | Document Studio | — | python-docx, python-pptx, openpyxl, PDF writer | Generated files re-open and validate | PDF writer | 1–2 weeks |
| 11 | Data Studio | — | pandas/polars, Recharts/ECharts | CSV/XLSX import→chart→export; resource limits | — | 1–2 weeks |
| 12 | Coding Lab + workflows | Docker **or** E2B account (if execution wanted) | xyflow, mcp SDK, procrastinate | Workflow run with approval; execution disabled unless sandbox proven | Sandbox choice/cost | 2–3 weeks |
| 13 | OCR, audio, vision, KG, MCP hub, usage, security center, Evaluation Lab | Tesseract (OCR), others per module | mcp SDK; others to research | Each module meets Definition of Done | Provider choices | 3–5 weeks |
| 14 | Public beta hardening | Monitoring account (e.g., Sentry free tier) | sentry-sdk, gitleaks, pip-audit, npm audit | Release gates in `09_TESTING` pass in staging; backup restore tested | Privacy policy/terms text | 1–2 weeks |
| 15 | Public web beta | Hosting accounts | — | Production smoke tests pass; known limitations published | Hosting providers, domain | 3–5 days |
| 16 | Desktop | **Rust (rustup) + MSVC Build Tools** | Tauri 2 | Windows installer built and tested | Code signing | 1–2 weeks |
| 17 | Final audit + handover | — | — | Final evidence report | — | 3–5 days |

Rough total (INFERRED): roughly 5–8 months of focused work for all 25 modules. A Release A beta (Phases 1–7 plus a slice of 14–15) is roughly 6–10 weeks.

## Install list (nothing installed yet)

| Item | When | Why |
|---|---|---|
| Python 3.12 project venv (uv) | Phase 2 | Isolate from global 3.14 packages |
| pnpm via corepack (optional) | Phase 2 | If chosen over npm |
| GitHub CLI (optional) | Phase 2 | Repo/PR operations |
| PostgreSQL 17 or 18 server | Phase 4 | Required database |
| Email provider (test account) | Phase 5 | Verification and reset emails |
| AI provider keys (free tiers) | Phase 6 | Model access |
| Docker Desktop or E2B | Phase 12 | Only if code execution is approved |
| Tesseract | Phase 13 | OCR |
| Rust + MSVC Build Tools | Phase 16 | Tauri |
