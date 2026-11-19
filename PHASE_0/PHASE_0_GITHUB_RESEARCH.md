# PHASE 0 — GitHub Open-Source Research

- **Date of data:** 2026-11-20
- **Sources (live):** GitHub REST API `GET /repos/{owner}/{repo}` (stars, SPDX license, last push, archived flag, open issues); raw `LICENSE` files read directly for every repo GitHub reported as `NOASSERTION` or no license; PyPI JSON API and `npm view` for latest versions and Python requirements.
- **Not done in Phase 0 (deferred to Phase 1):** source-code inspection, CI/test review, security advisory lookup per package, transitive dependency audit, scorecards. Those are what Phase 1 is for in `11_PHASED_EXECUTION_PLAN.md`.
- **Legend:** VERIFIED = from the live sources above. INFERRED = engineering judgment, not measured. "Stars" are popularity only and were **not** used as a selection criterion on their own.

## 0. License red flags found (read first)

| Repo | License actually found | Impact on AURA |
|---|---|---|
| n8n-io/n8n | **Sustainable Use License** (not OSI open source); `.ee.` files need an enterprise license | Do **not** embed or offer as part of a hosted service. Reject. |
| open-webui/open-webui | **Open WebUI License**: BSD-style plus a clause forbidding removal of "Open WebUI" branding in deployments above a user threshold | Not suitable as a base for a rebranded "AURA" product. Reference only. |
| lobehub/lobe-chat (now lobehub/lobehub) | **LobeHub Community License**: Apache-2.0 plus a requirement for a commercial license to distribute derivative works | Reject as a base. Reference only. |
| pymupdf/PyMuPDF | **AGPL-3.0** | Network use triggers source disclosure. Use `pypdf` (BSD-3-Clause) instead. |
| searxng/searxng | **AGPL-3.0** | Usable only as a separate, unmodified service called over HTTP; obligations attach to SearXNG itself (INFERRED; needs legal review before adoption). |
| greensock/GSAP | **GSAP "Standard No Charge" license** (proprietary, free of charge), not an OSI license | Already in the approved stack. Terms at https://gsap.com/standard-license must be read and recorded before use in Phase 3. Framer Motion can cover most needs if terms are a problem. |
| BerriAI/litellm | MIT, **except `litellm/enterprise/`** (separate license) | Use only the MIT core; never import from `enterprise/`. |
| langfuse/langfuse | MIT, **except `ee/` directories** | Self-host MIT parts only if adopted. |
| psycopg/psycopg | **LGPL-3.0** | Fine to use as an unmodified dependency; record in register. |
| modelcontextprotocol/typescript-sdk | Transitioning MIT → Apache-2.0 (mixed) | Both permissive; record both. |

## 1. Shortlist by capability

Columns: Stars and last push are VERIFIED as of 2026-11-20. Version = latest on PyPI/npm (VERIFIED). Cost: "Free" means the software is free; any model/API it calls may not be.

### 1.1 Animated frontend (approved stack — confirmation)

| Repo | License | Stars | Last push | Latest pkg | Notes |
|---|---|---|---|---|---|
| https://github.com/facebook/react (now `react/react`) | MIT | 252,796 | 2026-11-19 | react 19.3.1 | Approved |
| https://github.com/vitejs/vite | MIT | 83,987 | 2026-11-19 | vite 8.3.8 | Approved |
| https://github.com/tailwindlabs/tailwindcss | MIT | 98,675 | 2026-11-18 | tailwindcss 4.3.5 | Approved; v4 config is CSS-first (INFERRED: shadcn init must match v4) |
| https://github.com/shadcn-ui/ui | MIT | 128,580 | 2026-11-19 | shadcn CLI 4.23.0 | Approved; copies components into repo (good for ownership) |
| https://github.com/motiondivision/motion | MIT | 35,371 | 2026-11-19 | motion 14.14.0 | "Framer Motion" is now published as `motion` |
| https://github.com/greensock/GSAP | GSAP Standard License | 30,952 | 2026-11-04 | gsap 3.15.1 | See §0 |
| https://github.com/mrdoob/three.js | MIT | 118,963 | 2026-11-19 | three 0.187.0 | Lazy-load only; GPU cost on low-end laptop |
| https://github.com/TanStack/query | MIT | 50,589 | 2026-11-19 | @tanstack/react-query 5.108.1 | Recommended for server state |

### 1.2 AI chat interface

| Repo | License | Stars | Last push | Fit for AURA |
|---|---|---|---|---|
| https://github.com/assistant-ui/assistant-ui | MIT | 13,340 | 2026-11-19 | **Shortlist.** React chat primitives (`@assistant-ui/react` 0.15.37), composable with shadcn/Tailwind, backend-agnostic. Pre-1.0 API (INFERRED risk of breaking changes). |
| https://github.com/vercel/ai | Apache-2.0 (license file read) | 28,092 | 2026-11-19 | Useful UI hooks (`ai` 7.0.177), but its server side is TypeScript; AURA's backend is Python, so only the client parts would apply (INFERRED). |
| open-webui, lobehub | see §0 | — | — | Reference for UX ideas only. |

### 1.3 Model integration / provider abstraction

| Repo | License | Stars | Last push | Latest pkg | Fit |
|---|---|---|---|---|---|
| https://github.com/BerriAI/litellm | MIT core (see §0) | 63,556 | 2026-11-19 | litellm 1.110.1 (py <3.16) | **Shortlist.** One API for 100+ providers incl. Gemini, Groq, OpenRouter, Cerebras, Anthropic, OpenAI (INFERRED from project docs; verify per provider). Very high issue count (5,306) suggests fast churn. Use as a library behind AURA's own adapter interface, not as the domain model. |
| https://github.com/pydantic/pydantic-ai | MIT | 21,295 | 2026-11-19 | pydantic-ai 2.71.0 | Alternative. Typed agents + multi-provider; fits Pydantic-heavy FastAPI code. |
| Official SDKs (`openai`, `anthropic`, `google-genai`, `groq`) | various permissive (verify) | — | — | — | Minimal-dependency alternative per enabled provider. |

### 1.4 Agent orchestration

| Repo | License | Stars | Last push | Latest pkg | Fit |
|---|---|---|---|---|---|
| https://github.com/langchain-ai/langgraph | MIT | 45,159 | 2026-11-19 | langgraph 1.2.23 | **Approved candidate, confirmed viable.** Graphs, checkpoints, human-in-the-loop interrupts, Postgres checkpointer (INFERRED from docs, verify package `langgraph-checkpoint-postgres`). Note: LangGraph Platform/Cloud is a paid service; only the OSS library is in scope. |
| https://github.com/pydantic/pydantic-ai | MIT | 21,295 | 2026-11-19 | 2.71.0 | Comparison candidate for Phase 1 ADR (simpler, less graph-oriented). |

### 1.5 Deep research

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/assafelovic/gpt-researcher | Apache-2.0 | 30,787 | 2026-11-12 | Reference architecture (planner → parallel researchers → report). Package `gpt-researcher` 0.17.0 requires Python ≥3.12. Heavy dependency tree (INFERRED). Better to study and reimplement the pattern on LangGraph than import wholesale. |
| https://github.com/langchain-ai/open_deep_research | MIT | 12,674 | 2026-08-10 | **ARCHIVED** (VERIFIED). Read for ideas only. |
| https://github.com/adbar/trafilatura | Apache-2.0 | 7,151 | 2026-11-18 | **Shortlist** for main-text extraction from fetched pages (trafilatura 2.3.1). |
| https://github.com/searxng/searxng | AGPL-3.0 | 39,714 | 2026-11-19 | Self-hosted meta-search; free but AGPL and needs a server (see §0). |

### 1.6 Browser automation

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/microsoft/playwright-python | Apache-2.0 | 15,120 | 2026-11-19 | **Shortlist** for E2E tests now (playwright 1.65.2; Chromium already on this machine). |
| https://github.com/browser-use/browser-use | MIT | 121,515 | 2026-11-19 | LLM browser agent (browser-use 1.0.6). Out of approved scope today (see conflict C1). Heavy: real Chromium per task, prompt-injection exposure. |

### 1.7 Coding agents and sandboxes

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/OpenHands/OpenHands (redirected from All-Hands-AI) | MIT | 93,849 | 2026-11-19 | Reference only; requires Docker and large resources (INFERRED). Too heavy for 8 GB laptop. |
| https://github.com/e2b-dev/E2B | Apache-2.0 | 14,934 | 2026-11-19 | Open-source SDK, but the sandbox runs on E2B's **cloud service (account, quotas, paid tiers)**. Self-hosting is non-trivial (INFERRED). Requires owner approval under cost rules. |
| Docker-based local sandbox | — | — | — | Free, but Docker is not installed and is RAM-heavy. Until a sandbox is proven, Coding Lab is code-assistance only (as `08_SECURITY` requires). |

### 1.8 MCP integrations

| Repo | License | Stars | Last push | Latest pkg | Fit |
|---|---|---|---|---|---|
| https://github.com/modelcontextprotocol/python-sdk | MIT | 24,908 | 2026-11-17 | mcp 2.3.0 | **Shortlist** for the backend MCP client in M14. |
| https://github.com/modelcontextprotocol/typescript-sdk | MIT/Apache-2.0 (mixed) | 13,788 | 2026-11-19 | @modelcontextprotocol/sdk 1.32.2 | Only if MCP is needed in the frontend/desktop. |

### 1.9 RAG, knowledge retrieval, persistent memory

| Repo | License | Stars | Last push | Latest pkg | Fit |
|---|---|---|---|---|---|
| https://github.com/xhluca/bm25s | MIT | 1,828 | 2026-11-13 | bm25s 0.3.16 | Fast BM25 in Python; alternative is PostgreSQL full-text search (built-in, zero new deps, INFERRED best first step). |
| https://github.com/pgvector/pgvector | PostgreSQL License (permissive, file read) | 23,738 | 2026-11-19 | — | **Shortlist** for later semantic search inside the same PostgreSQL; avoids a separate vector DB. Requires the extension on the host (most managed Postgres offer it, verify per host). |
| https://github.com/qdrant/qdrant | Apache-2.0 | 35,638 | 2026-11-19 | — | Separate service; only if pgvector proves insufficient. |
| https://github.com/mem0ai/mem0 | Apache-2.0 | 69,248 | 2026-11-18 | mem0ai 2.2.1 | Memory layer reference. AURA's memory needs strict user/project separation and user controls; owning the tables in PostgreSQL may be simpler than adopting mem0 (INFERRED; decide in Phase 1). |
| chromadb (already installed globally) | Apache-2.0 (verify) | — | — | — | Not needed if pgvector is chosen. |

### 1.10 Conversation summarization

No dedicated repo needed. Summarization is an LLM call with a structured Pydantic output schema (fields listed in `06_CHAT_MEMORY_LANGUAGE.md`), triggered by token estimates. LangGraph and LiteLLM both expose token counting helpers (INFERRED; verify in Phase 7).

### 1.11 Multilingual (English, Urdu, Roman Urdu, mixed)

| Repo | License | Stars | Last push | Latest pkg | Fit |
|---|---|---|---|---|---|
| https://github.com/pemistahl/lingua-py | Apache-2.0 | 1,820 | 2026-07-20 | lingua-language-detector 2.2.0 (py ≥3.12) | **Shortlist** for script-based detection (Urdu in Arabic script, English). It does **not** list Roman Urdu as a language (INFERRED from its language list; verify). |

Roman Urdu requires an AURA-specific layer: a word-list heuristic plus an LLM classification fallback, tested with real mixed samples. Response language can largely be handled by instructing the model with the detected style.

### 1.12 Document generation

| Repo / package | License | Stars | Last activity | Fit |
|---|---|---|---|---|
| https://github.com/python-openxml/python-docx | MIT | 5,774 | push 2026-08-01, release 1.2.0 (2025-06-16) | **Shortlist** DOCX |
| https://github.com/scanny/python-pptx | MIT | 3,590 | **last push 2024-08-07**, release 1.0.2 (2024-08-07) | **Shortlist with risk**: no activity for ~27 months. Still the standard Python PPTX library. |
| openpyxl (source on foss.heptapod.net, not GitHub) | MIT | n/a | release 3.1.5 (2024-06-28) | **Shortlist** XLSX; slow release cadence |
| https://github.com/py-pdf/pypdf | BSD-3-Clause (file read) | 10,303 | 2026-11-19, pypdf 7.1.1 | PDF reading/manipulation |
| PDF generation | — | — | — | Not chosen yet (candidates for Phase 1: ReportLab (BSD, verify), WeasyPrint (BSD, verify; needs GTK on Windows)). |

### 1.13 Data analysis and visualization

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| pandas (installed 3.0.5) | BSD-3 (verify) | — | — | Default for CSV/XLSX |
| https://github.com/pola-rs/polars | MIT | 40,386 | 2026-11-19 | Faster, lower memory; polars 2.1.0 |
| https://github.com/recharts/recharts | MIT | 27,722 | 2026-11-19 | React-native charts, easy theming |
| https://github.com/apache/echarts | Apache-2.0 | 67,755 | 2026-10-13 | Richer charts and animation; heavier bundle |

### 1.14 Workflow automation

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/xyflow/xyflow | MIT | 39,088 | 2026-11-19 | **Shortlist** visual node editor (`@xyflow/react` 13.0.2) |
| https://github.com/procrastinate-org/procrastinate | MIT | 1,459 | 2026-11-19 | **Shortlist** PostgreSQL-based job queue (3.12.0): no Redis needed, saves RAM and a paid service |
| n8n | see §0 | — | — | Rejected (license) |

### 1.15 Authentication

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/fastapi-users/fastapi-users | MIT | 6,261 | 2026-11-18 | **Maintenance mode** (README, VERIFIED): security fixes only, a successor is planned. Usable but a long-term risk. |
| https://github.com/supabase/auth | MIT | 2,604 | 2026-11-17 | Hosted via Supabase (free tier with limits, verify) or self-hosted Go service. Handles email verification, OAuth, MFA. |
| Self-built on FastAPI with argon2-cffi + PyJWT | permissive (verify) | — | — | Full control, more security surface to own and test. |

### 1.16 Database architecture

| Repo | License | Stars | Last push | Latest pkg |
|---|---|---|---|---|
| https://github.com/fastapi/fastapi | MIT | 104,924 | 2026-11-18 | fastapi 0.165.0 (py ≥3.11) |
| https://github.com/sqlalchemy/sqlalchemy | MIT | 12,295 | 2026-11-19 | sqlalchemy 2.1.9 |
| https://github.com/sqlalchemy/alembic | MIT | 4,481 | 2026-10-30 | alembic 1.20.1 |
| https://github.com/psycopg/psycopg | LGPL-3.0 | 2,535 | 2026-11-18 | psycopg 3.3.9 (async capable) |

All approved choices are active and permissively licensed (psycopg LGPL is acceptable as a dependency).

### 1.17 Desktop

| Repo | License | Stars | Last push | Latest pkg |
|---|---|---|---|---|
| https://github.com/tauri-apps/tauri | Apache-2.0 (npm CLI: Apache-2.0 OR MIT) | 113,006 | 2026-11-19 | @tauri-apps/cli 2.12.6 |

Approved choice confirmed active. Requires Rust and MSVC Build Tools (both missing on this machine).

### 1.18 Supporting: rate limiting, monitoring, LLM observability

| Repo | License | Stars | Last push | Fit |
|---|---|---|---|---|
| https://github.com/laurentS/slowapi | MIT | 2,070 | 2026-11-18 | Rate limiting for FastAPI (0.1.10, still 0.x) |
| https://github.com/getsentry/sentry-python | MIT | 2,218 | 2026-11-19 | Error monitoring SDK; Sentry SaaS has a free tier with limits (verify) |
| https://github.com/langfuse/langfuse | MIT core (see §0) | 37,641 | 2026-11-19 | LLM tracing/evals; self-host is heavy (INFERRED), cloud has free tier (verify) |

## 2. Free vs. paid summary

| Free software, runs locally or on own host | Free SDK, but needs an external service with quotas/paid tiers |
|---|---|
| React, Vite, Tailwind, shadcn/ui, Motion, Three.js, TanStack Query, assistant-ui, FastAPI, SQLAlchemy, Alembic, psycopg, LangGraph (library), LiteLLM (core), Pydantic AI, MCP SDKs, bm25s, pgvector, trafilatura, Playwright, python-docx, python-pptx, openpyxl, pypdf, polars, Recharts, ECharts, xyflow, procrastinate, slowapi, Tauri, lingua | AI model APIs (all), E2B cloud sandbox, Supabase hosted, Sentry SaaS, Langfuse cloud, LangGraph Platform, web search APIs |

## 3. Items that need verification in Phase 1

1. Current free-tier quotas and terms for Gemini, Groq, OpenRouter, Cerebras (not verified in Phase 0).
2. GSAP Standard License full text.
3. Security advisories (GitHub Advisory DB / OSV) for every shortlisted package.
4. Python 3.12/3.13 wheel availability for each backend package.
5. Hosting free tiers (Vercel, Render, Supabase or alternatives): sleep behaviour, limits, pgvector availability.
6. Roman Urdu coverage of any detector.
