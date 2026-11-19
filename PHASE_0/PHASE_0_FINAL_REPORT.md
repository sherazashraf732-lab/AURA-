# PHASE 0 — Final Report

- **Phase:** 0 — Master project inspection and open-source research
- **Date:** 2026-11-20
- **Decision:** PASS (inspection and research complete). No implementation was attempted.
- **Files created:** the eight `PHASE_0/PHASE_0_*.md` reports only. No existing file was modified, moved or deleted. Nothing was installed, pushed or deployed.

## 1. What already exists

- A complete **specification package** of 23 files: master rules, 12 design docs, feature matrix, manifest, acceptance checklist, templates, `.env.example` and `.gitignore`.
- **No code**, no Git repository, no dependencies, no tests, no deployments. The acceptance checklist is entirely unchecked.
- Clear approved decisions: modular monolith; React/TS/Vite/Tailwind/shadcn/Motion (+ selective GSAP/Three.js); FastAPI/Pydantic/SQLAlchemy/Alembic/PostgreSQL; LangGraph candidate; provider-neutral adapters; BM25 first; web beta first, Tauri later; paid usage off by default; 20 core modules + 5 additions.

Details: `PHASE_0_EXISTING_PROJECT_AUDIT.md`.

## 2. What is missing

**Spec decisions:** AURA's own license; web search provider; email provider; object storage; auth approach; job queue; code sandbox; PDF writer; context thresholds; retention policy; privacy policy and terms; admin bootstrap and MFA method; quota numbers; UI i18n; accessibility target; monitoring provider; domain.

**Spec conflicts to resolve (C1–C6):** browser automation scope; GitHub research timing (Phase 0 vs. 1); status files timing; kickoff "continue" vs. "stop after phase"; audio/vision vs. "voice/video future"; Evaluation Lab vs. Evaluation Center overlap.

**Language:** Roman Urdu is not explicitly specified and needs custom handling.

## 3. Environment condition

| Area | Status |
|---|---|
| OS | Windows 11 Pro Education 10.0.26300, 64-bit |
| Hardware | i3-1215U (6C/8T), **7.64 GB RAM (0.76 GB free at audit)**, **35.6 GB free disk** |
| Ready | Git 2.55.0, Node 24.19.0 (nvm, 26.7.0 also), npm 11.17.0, corepack, Python 3.14.6 + 3.12, uv 0.13.6, VS Code 1.144.0, winget, FFmpeg 9.0.2, Playwright Chromium, WebView2 |
| Missing | GitHub CLI, PostgreSQL server (only a leftover PG 18 data folder exists), Docker, WSL, Redis, Rust/cargo, MSVC Build Tools, Tesseract, pnpm |
| Concern | Global Python 3.14 has 291 packages incl. torch/transformers; AURA must use an isolated uv environment on Python 3.12 |

Details: `PHASE_0_ENVIRONMENT_AUDIT.md`.

## 4. Recommended technologies

The approved stack stands; **no replacement is recommended.** All approved components were verified live as active and permissively licensed (GSAP has its own no-charge license that must be read). Proposed fills for open gaps (to confirm by ADR in Phase 1):

- Python 3.12 + uv; npm or pnpm via corepack.
- TanStack Query, React Router, assistant-ui for chat.
- AURA provider adapter with LiteLLM (MIT core) underneath, plus a deterministic mock provider.
- LangGraph for orchestration (compare with Pydantic AI as the spec requires).
- procrastinate (PostgreSQL job queue) to avoid Redis.
- PostgreSQL full-text search first, pgvector later.
- trafilatura for page extraction; search provider via adapter.
- lingua + custom Roman Urdu layer.
- python-docx, python-pptx, openpyxl, pypdf; PDF writer to be chosen.
- pandas/polars, Recharts (ECharts if needed), xyflow, official `mcp` SDK.
- slowapi + DB quotas, Sentry SDK, Playwright, ruff/mypy/ESLint.

Details: `PHASE_0_TECH_STACK_EVALUATION.md`.

## 5. GitHub projects that can be integrated

Integrate as packages (licenses verified live): React, Vite, Tailwind CSS, shadcn/ui, Motion, Three.js, TanStack Query, assistant-ui, FastAPI, SQLAlchemy, Alembic, psycopg (LGPL dependency), LangGraph, LiteLLM (core only), Pydantic AI, MCP Python SDK, bm25s, pgvector, trafilatura, Playwright, python-docx, python-pptx, openpyxl, pypdf, polars, Recharts, ECharts, xyflow, procrastinate, slowapi, sentry-python, Tauri, lingua-py.

**Reference only / rejected:** n8n (Sustainable Use License), Open WebUI (branding clause), LobeHub (derivative-work restriction), PyMuPDF (AGPL), open_deep_research (archived), OpenHands (too heavy), browser-use (out of approved scope). SearXNG (AGPL) and E2B (cloud quotas/paid) need owner decisions.

Details: `PHASE_0_GITHUB_RESEARCH.md`.

## 6. What needs installation (later, each with approval)

Phase 2: uv project venv on Python 3.12; optional `gh`, pnpm. Phase 4: PostgreSQL server. Phase 5: email provider test account. Phase 6: free-tier AI keys. Phase 12: Docker or E2B only if execution is approved. Phase 13: Tesseract. Phase 16: Rust + MSVC Build Tools.

## 7. Estimated development stages

The approved Phases 1–17 are kept (`PHASE_0_IMPLEMENTATION_ROADMAP.md`). Rough estimate (INFERRED): Release A beta in about 6–10 weeks; all modules in about 5–8 months.

## 8. Risks needing attention

Top risks: scope size (R01), low RAM (R02), free-quota volatility and accidental paid usage (R04/R05), bot signups (R06), cross-tenant leaks (R07), prompt injection (R08), restrictive licenses (R10), Roman Urdu accuracy (R14), free hosting limits (R15), missing legal docs (R19), object storage not chosen (R24). Full list: `PHASE_0_RISK_REGISTER.md`. Security gaps S1–S14: `PHASE_0_SECURITY_REVIEW.md`.

## 9. What should happen in Phase 1 (after approval)

1. Owner resolves conflicts C1–C6 and chooses AURA's license.
2. Deepen research: inspect source, CI, tests and security advisories (OSV/GitHub Advisory DB) for each shortlisted package; score with the 10-point scorecard.
3. Verify current free tiers for AI providers, search, email, object storage and hosting.
4. Write ADRs: orchestration (LangGraph vs. Pydantic AI), provider layer, auth option, job queue, search provider, PDF writer, chart library, Roman Urdu approach.
5. Create `OPEN_SOURCE_REGISTER.md`, `DECISIONS.md`, `BUILD_STATUS.md`, `TEST_REPORT.md`, `KNOWN_ISSUES.md`.
6. Read and record the GSAP license decision.
7. Add the security gaps S1–S14 to the security spec.

## 10. Verification notes

- GitHub stars, licenses, last-push dates and archived flags came from the live GitHub REST API on 2026-11-20. License files were read directly where GitHub reported none or `NOASSERTION`.
- Package versions came from live PyPI and npm.
- Free-tier quotas, hosting limits and security advisories were **not** verified in this phase.
- Everything labeled INFERRED is judgment, not measurement.

PHASE 0 COMPLETED — AWAITING HUMAN APPROVAL.
