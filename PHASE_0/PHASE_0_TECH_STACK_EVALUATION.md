# PHASE 0 — Tech Stack Evaluation

- **Date:** 2026-11-20
- **Basis:** Approved architecture (`docs/02_ARCHITECTURE.md`, `aura_manifest.json`), live data in `PHASE_0_GITHUB_RESEARCH.md`, machine facts in `PHASE_0_ENVIRONMENT_AUDIT.md`.
- **Outcome:** **No approved technology needs to be replaced.** All approved components are actively maintained and permissively licensed, with one licensing note (GSAP). Recommendations below fill the gaps the spec left open; each is a proposal for a Phase 1 ADR, not a final decision.

## 1. Approved stack — verdict

| Layer | Approved | Verdict | Evidence / note |
|---|---|---|---|
| UI framework | React + TypeScript | KEEP | MIT, pushed 2026-11-19, react 19.3.1 |
| Build | Vite | KEEP | MIT, vite 8.3.8 |
| Styling | Tailwind CSS | KEEP | MIT, v4.3.5 (CSS-first config) |
| Components | shadcn/ui | KEEP | MIT, CLI 4.23.0 |
| Motion | Framer Motion | KEEP (package is now `motion` 14.14.0) | MIT |
| Choreography | GSAP | KEEP, CONDITIONAL | Proprietary no-charge license; read terms before Phase 3. If unacceptable, use Motion only. |
| 3D | Three.js | KEEP, LIMITED | MIT; lazy-load, off in Reduced/Off modes; low-end iGPU on this laptop (i3-1215U) |
| API | FastAPI | KEEP | MIT, 0.165.0, py ≥3.11 |
| ORM / migrations | SQLAlchemy 2.x + Alembic | KEEP | MIT, 2.1.9 / 1.20.1 |
| DB | PostgreSQL | KEEP | Not installed locally yet |
| Driver | psycopg 3 | KEEP (spec's own suggestion) | LGPL-3.0 as an unmodified dependency; async support |
| Orchestration | LangGraph | KEEP, confirm by ADR | MIT, 1.2.23, checkpoints + human approval fit A03/M03; compare with Pydantic AI in Phase 1 as required by the spec |
| Desktop | Tauri | KEEP (later) | Apache-2.0/MIT, needs Rust + MSVC |

## 2. Proposed choices for open gaps (to confirm in Phase 1 ADRs)

| Gap | Proposal | Why | Alternative |
|---|---|---|---|
| Python version | **3.12** (installed) or 3.13 via `uv` | 3.14 is the global default but very new; lingua and gpt-researcher need ≥3.12; widest wheel coverage | 3.13 |
| Python tooling | **uv** (installed) + `uv.lock` | Already on machine; spec suggests `uv.lock` | Poetry (not installed) |
| JS package manager | **pnpm via corepack** or plain npm | Spec suggests pnpm; corepack is present so no separate installer (INFERRED) | npm (already works) |
| Server state | TanStack Query | MIT, active, spec suggests it | SWR |
| Routing | React Router (verify current version in Phase 2) | Spec suggests it | TanStack Router |
| Forms | react-hook-form + zod (verify licenses) | Common with shadcn/ui (INFERRED) | — |
| Chat UI | **assistant-ui** | MIT, React + shadcn style, backend-agnostic | Build on shadcn primitives |
| Provider abstraction | **AURA adapter interface + LiteLLM (MIT core) underneath** | One call shape for Gemini/Groq/OpenRouter/Cerebras/Anthropic/OpenAI; adapter keeps vendor out of domain logic | Official SDKs per provider |
| Mock provider | Custom deterministic adapter | Required by spec for tests | — |
| Job queue | **procrastinate** (PostgreSQL-backed) | No Redis process or paid Redis host; saves RAM on 8 GB machine | ARQ/Celery + Redis |
| Live progress | SSE first | Simpler than WebSocket for one-way agent status | WebSocket |
| Keyword retrieval | **PostgreSQL full-text search** first, bm25s if ranking quality is insufficient | Zero new services | rank-bm25 (older) |
| Semantic retrieval (later) | **pgvector** | Same database, permissive license | Qdrant |
| Memory | Own tables in PostgreSQL (user_memories, project_memories, conversation_summaries) | Spec requires strict separation and user controls | mem0 as a library |
| Web extraction | trafilatura | Apache-2.0, active | BeautifulSoup + readability |
| Web search | Provider adapter; start with a free-tier search API or self-hosted SearXNG (AGPL, separate service) — owner choice | Needed for M01; no free unlimited option exists (INFERRED) | — |
| Language detection | lingua + custom Roman Urdu layer + LLM fallback | lingua covers script-based languages; Roman Urdu needs custom handling | fastText LID (verify license) |
| DOCX / PPTX / XLSX | python-docx / python-pptx / openpyxl | MIT; de facto standards. python-pptx inactive since 2024-08 (risk recorded) | — |
| PDF read | pypdf (BSD-3) | Avoid AGPL PyMuPDF | — |
| PDF write | Decide in Phase 1 (ReportLab vs. WeasyPrint vs. DOCX→PDF) | Needs license and Windows dependency check | — |
| Data | pandas (default) + polars where memory matters | Both permissive | — |
| Charts | Recharts (default) | Simple React theming; ECharts if richer charts are needed | ECharts |
| Workflow editor | xyflow (`@xyflow/react`) | MIT, active | — |
| MCP | `mcp` Python SDK | MIT, official | — |
| Auth | **Decision for owner** (see below) | — | — |
| Rate limiting | slowapi + per-user quotas in DB | MIT; DB quotas survive restarts | Gateway-level limits |
| Error monitoring | Sentry SDK (free tier limits to verify) | MIT SDK | GlitchTip (verify license) |
| E2E tests | Playwright | Apache-2.0; Chromium already present | — |
| Lint/type | ruff + mypy (Python), ESLint + TypeScript (web) | Spec suggests these | pyright |
| Code sandbox | **Disabled until proven**; candidates Docker-based local, or E2B cloud (needs paid/free-tier approval) | Spec rule | — |

### Auth decision (owner's choice)

| Option | Pros | Cons |
|---|---|---|
| A. Self-built FastAPI auth (argon2 + JWT/sessions + email provider) | No vendor lock-in; data stays in AURA's PostgreSQL | AURA owns all security of signup, reset, MFA, session rotation; more tests |
| B. fastapi-users | Faster start, MIT | **Maintenance mode**; successor planned |
| C. Supabase Auth (hosted) | Email verification, OAuth, MFA handled; free tier exists (verify) | External dependency; quotas; ties DB choice to Supabase |

**Recommendation:** C if Supabase is also chosen for PostgreSQL hosting; otherwise A. Avoid B for a new long-lived project.

## 3. Hosting candidates (not verified this phase)

The spec lists Vercel (frontend), Render (API/worker) and Supabase (DB/auth/storage). Free tiers change often and were **not** verified in Phase 0. Known concerns to check (INFERRED): free web services that sleep after inactivity, free databases that pause or expire, and background workers that are not free on some hosts. A PostgreSQL-backed queue lets the API and worker share one database, which reduces the number of free services needed.

## 4. What this machine can run during development (INFERRED)

| Workload | Feasible on 8 GB? |
|---|---|
| Vite dev server + FastAPI + native PostgreSQL | Yes, with browser and VS Code, if other apps are closed |
| Docker Desktop + containers | Marginal; avoid until Phase 12 |
| Local LLMs (Ollama etc.) | No (spec also says avoid) |
| Playwright E2E (1 browser, serial) | Yes |
| Tauri build (Rust compile) | Slow but possible; Phase 16 only |
