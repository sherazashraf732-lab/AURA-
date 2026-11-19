# PHASE 1 — Architecture Decision Records (DRAFT)

- **Date:** 2026-11-20
- **Status key:** `ACCEPTED (spec)` = already approved in the package, recorded here only. `PROPOSED` = Claude's recommendation, awaiting owner review. `OWNER DECISION` = cannot be finalized without the owner's choice. **Nothing below is final until Sammer approves.**
- Evidence references: `PHASE_0_GITHUB_RESEARCH.md`, `PHASE_1_DEEP_RESEARCH.md`, `PHASE_1_FREE_TIER_VERIFICATION.md`.

---

## ADR-001 — Modular monolith with background worker
- **Status:** ACCEPTED (spec)
- **Decision:** One FastAPI application with domain modules under `backend/app/modules/*`, one worker process, one React web app. No microservices.
- **Consequences:** Simple deploys on free hosts; module boundaries enforced by code structure and tests.

## ADR-002 — Agent orchestration: LangGraph
- **Status:** PROPOSED
- **Context:** Spec names LangGraph as candidate and requires comparing alternatives. Needs: bounded multi-step agents, checkpoints, cancellation, human approval, budgets (M03, A03, M01).
- **Options:** (a) LangGraph 1.2.x (MIT); (b) Pydantic AI 2.71 (MIT); (c) custom state machine.
- **Comparison:**

| Criterion | LangGraph | Pydantic AI |
|---|---|---|
| Graph/state-machine workflows | Native | Supported, less central |
| Persisted checkpoints | Built-in checkpointer interface; `libs/checkpoint-postgres` exists in the repo (VERIFIED) | Less mature (INFERRED) |
| Human-in-the-loop interrupts | Native `interrupt` | Possible via tool approval |
| Typing / Pydantic fit | Good | Excellent |
| Dependency weight | Pulls `langchain-core` (18 historical advisories, none in current version) | Lighter (INFERRED) |
| Activity | 275 commits / 26 authors in 90 days (VERIFIED) | Very active (VERIFIED push 2026-11-19) |
| Advisories affecting current version | None (OSV) | None (OSV) |

- **Decision:** Use LangGraph for multi-step agents and research graphs. Do not use LangChain's higher-level chains or integrations beyond what LangGraph needs. Do not use LangGraph Platform (paid).
- **Consequences:** Pin versions; wrap LangGraph behind an `AgentRunner` interface so it can be replaced.

## ADR-003 — Model provider abstraction
- **Status:** PROPOSED
- **Decision:** AURA defines its own `ModelProvider` interface (chat, stream, count_tokens, capabilities, usage). The first implementation wraps **LiteLLM (MIT core only, never `litellm/enterprise/`)**; a deterministic `MockProvider` serves all automated tests. LiteLLM is used as a Python library only, **not** its proxy server.
- **Why:** One code path for Gemini, Groq, OpenRouter, Cerebras and paid providers; keeps vendor code out of domain logic.
- **Risks:** LiteLLM has 85 historical advisories (none in 1.110.1) and very high churn → pin exact version, upgrade deliberately, run adapter contract tests on each upgrade. Fallback plan: replace with official SDKs behind the same interface.
- **Mandatory rules:** quota is global per provider account; per-user caps below it; never auto-switch to a paid provider; paid providers require `ALLOW_PAID_PROVIDER_USAGE=true` **and** admin consent.

## ADR-004 — Authentication approach
- **Status:** OWNER DECISION (see Phase 1 report, decision D-AUTH)
- **Options:** A self-built (argon2-cffi + server-side sessions, own email sending); B fastapi-users (maintenance mode, VERIFIED); C Supabase Auth (hosted; free plan 50,000 MAU; project pauses after 1 week inactivity).
- **Recommendation:** **A**, with server-side sessions in PostgreSQL (HTTP-only, Secure, SameSite cookies + CSRF token). Reason: keeps one database, no pausing risk, full control of tenant isolation; argon2-cffi has no known advisories. Choose C only if Supabase is also chosen for the database.
- **Note:** PyJWT has 48 historical advisories; server-side sessions avoid needing JWTs for the web app.

## ADR-005 — Background job queue
- **Status:** PROPOSED
- **Decision:** **procrastinate** (MIT, PostgreSQL-backed, 3.12.0, no known advisories).
- **Why:** No Redis server locally (saves RAM) or in hosting (saves a service); jobs live in the same DB, so job state and task tables can share transactions.
- **Alternatives rejected for now:** Celery/ARQ + Redis (extra service), FastAPI BackgroundTasks (not durable).

## ADR-006 — Retrieval for Knowledge Base / RAG
- **Status:** PROPOSED (consistent with spec)
- **Decision:** Stage 1: PostgreSQL full-text search (`tsvector`, per-user/project filters). Stage 2 (after evaluation in Evaluation Lab): **pgvector** in the same database. bm25s only if Postgres ranking proves inadequate.
- **Note:** Postgres FTS has no Urdu dictionary (INFERRED); use the `simple` configuration for Urdu and Roman Urdu text, and test retrieval quality.

## ADR-007 — Memory and conversation continuation
- **Status:** PROPOSED (implements spec 06)
- **Decision:** Three separate tables and services: `user_memories`, `project_memories`, `conversation_summaries` (versioned, linked to source messages). Own implementation in PostgreSQL rather than mem0 (mem0 has 10 historical advisories; more importantly AURA needs strict user controls and separation that are simpler to own).
- **Continuation trigger:** token estimate ≥ a configurable fraction of the selected model's context window (default proposal 75%, with reserved space for the reply). Summary is a structured Pydantic object with the fields listed in spec 06. Original chat is never modified.
- **User controls:** view, edit, disable (per user and per chat), delete for memories and summaries; memory saving off for sensitive categories by default.

## ADR-008 — Language detection (English, Urdu, Roman Urdu, mixed)
- **Status:** PROPOSED
- **Decision:** Three layers:
  1. **Script detection** (Unicode ranges) → Arabic-script Urdu vs. Latin.
  2. **lingua-py** (Apache-2.0) for Latin-script language identification.
  3. **Roman Urdu classifier**: AURA-owned word-frequency heuristic (common Roman Urdu tokens such as "hai", "nahi", "kya", "mujhe") producing a score; ambiguous cases resolved by the model itself via the system prompt ("reply in the user's language and script").
- **Output:** `{language: en|ur|ur-Latn|mixed, script, style: formal|casual}` stored per message; account and chat overrides win.
- **Tests:** A labeled corpus of at least 200 short messages (English, Urdu, Roman Urdu, mixed, ambiguous) created in Phase 7; target accuracy to be set by owner.
- **Note:** lingua 2.2.0 requires Python ≥3.12 (VERIFIED), consistent with ADR-015.

## ADR-009 — Document generation
- **Status:** PROPOSED
- **Decision:** python-docx (DOCX), python-pptx (PPTX), openpyxl (XLSX) behind a `DocumentRenderer` interface with an intermediate content model. PDF output: **ReportLab** (BSD, pure Python wheels on Windows, INFERRED) as default; WeasyPrint rejected for Windows dev because it needs GTK/Pango system libraries (INFERRED; WeasyPrint also has 10 historical advisories).
- **Risk:** python-pptx inactive since 2024-08 (VERIFIED). Mitigation: isolate behind interface; validate every generated file by re-opening it.
- **Untrusted inputs:** parsing user-uploaded OOXML/PDF happens only in the worker with size/time limits; pypdf has 119 historical advisories (mostly parser DoS, none in 7.1.1) → always latest pypdf + resource limits.

## ADR-010 — Data Studio and charts
- **Status:** PROPOSED
- **Decision:** pandas for analysis (polars optional for large files), **Recharts** for charts in the UI (MIT, React-native, themable with design tokens). ECharts only if a chart type is missing.

## ADR-011 — Chat UI
- **Status:** PROPOSED
- **Decision:** **assistant-ui** (MIT) primitives styled with shadcn/ui and AURA tokens, connected to AURA's own SSE endpoint. Rendered model markdown is sanitized (DOMPurify or equivalent; DOMPurify has frequent advisories → keep latest).
- **Risk:** pre-1.0 API → pin and wrap.

## ADR-012 — Web search for AI Research
- **Status:** OWNER DECISION (D-SEARCH)
- **Options:** Tavily free 1,000 credits/month, no card (VERIFIED); Brave $5 free credits/month, card required, no result storage (VERIFIED); self-hosted SearXNG (AGPL, needs a server).
- **Recommendation:** `SearchProvider` interface; start with **Tavily free** for development and the beta, with per-user daily search caps; fixtures for tests.

## ADR-013 — Hosting, database host, object storage
- **Status:** OWNER DECISION, deferred to Phase 14 re-verification
- **Findings:** Vercel Hobby is **personal/non-commercial only** (VERIFIED, Terms §4). Supabase free pauses after 1 week inactivity. Neon free: 1 GB/project, scale-to-zero, pgvector included. Cloudflare R2: 10 GB free, no egress fees. Render free tier **could not be verified** (site unreachable).
- **Proposed direction:** web on Vercel Hobby while the beta is free and non-commercial; Postgres on Neon or Supabase; files on R2; API/worker host to be verified.

## ADR-014 — Code execution sandbox
- **Status:** PROPOSED
- **Decision:** **Code execution disabled** in beta. Coding Lab offers explanation, generation, review and test-writing only. Revisit in Phase 12 with Docker-based or E2B (cloud, quota/paid) sandboxes, each requiring owner approval.

## ADR-015 — Toolchain versions
- **Status:** PROPOSED
- **Decision:** Python **3.12** via `uv` with `uv.lock` (3.12 installed; several deps need ≥3.11/3.12); Node 24 LTS; **npm** (already installed, avoids adding pnpm) with `package-lock.json`. Revisit pnpm only if a monorepo workspace needs it.

## ADR-016 — Animation libraries
- **Status:** PROPOSED
- **Decision:** Motion (`motion` package, MIT) for all standard UI motion; Three.js lazy-loaded only for the hero/startup scene; **GSAP optional** — used only if a sequence cannot be done well with Motion, and only after the owner accepts the GSAP license (see owner decision L note).

## ADR-017 — Security baseline
- **Status:** PROPOSED
- **Decision:** Deny-by-default authorization; ownership filters in every repository method; IDOR test per endpoint; CSP + security headers; CORS allowlist; CSRF tokens with cookie sessions; SSRF guard for fetcher and MCP; upload magic-byte checks and limits; secret scanning (gitleaks) + `pip-audit` + `npm audit` in CI; encrypted provider keys (envelope encryption); append-only audit log. Details: `PHASE_0_SECURITY_REVIEW.md` S1–S14.

## ADR-018 — AURA license
- **Status:** OWNER DECISION (L)
- **Recommendation:** Proprietary, all rights reserved, private repository during beta. See `PHASE_1_OWNER_DECISIONS.md`.
