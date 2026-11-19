# PHASE 0 — Risk Register

- **Date:** 2026-11-20
- **Scale:** Likelihood (L) and Impact (I) as Low / Medium / High. Status for all: OPEN.

| ID | Risk | L | I | Evidence | Mitigation | Owner |
|---|---|---|---|---|---|---|
| R01 | Scope too large for one developer (25 modules) | High | High | 20 core + 5 additions; no code yet | Ship Release A first; strict Definition of Done per module; defer non-essential modules | Owner |
| R02 | 8 GB RAM, under 1 GB free during audit | High | Medium | Environment audit | Native PostgreSQL, no Docker until needed, no local LLMs, serial test runs, close other apps | Dev |
| R03 | Python 3.14 compatibility gaps | Medium | Medium | Global default is 3.14.6 | Use Python 3.12 via uv for AURA | Dev |
| R04 | Free AI provider quotas change or end | High | High | Free tiers not verified; terms change often (INFERRED) | Provider adapter, mock provider, quota display, no paid fallback, multiple free providers | Dev |
| R05 | Accidental paid usage | Medium | High | Many SDKs default to paid keys | `ALLOW_PAID_PROVIDER_USAGE=false`, global cap 0, explicit consent UI, tests for quota exhaustion | Dev |
| R06 | Bot signups exhaust free quotas | High | High | Open registration planned | Email verification before use, CAPTCHA/PoW, per-user caps, admin suspension | Dev |
| R07 | Cross-tenant data exposure | Medium | High | Multi-user memory, files, chats | Owner filters in repositories, IDOR test suite, optional Postgres RLS | Dev |
| R08 | Prompt injection via web pages/documents | High | High | Research + RAG + MCP | Treat content as data, tool allowlists, approvals, no side-effect tools in beta | Dev |
| R09 | Unsafe code execution | Medium | High | Coding Lab | Execution disabled until sandbox proven | Dev |
| R10 | Copyleft/restrictive licenses enter the codebase | Medium | High | AGPL (PyMuPDF, SearXNG), n8n SUL, Open WebUI branding, LobeHub | Register, CI license scan, reject list from Phase 0 | Dev |
| R11 | GSAP license terms unacceptable | Low | Low | Proprietary no-charge license | Read terms in Phase 3; Motion fallback | Owner |
| R12 | Unmaintained dependencies (python-pptx since 2024-08, openpyxl release 2024-06, fastapi-users maintenance mode) | Medium | Medium | Live GitHub/PyPI data | Pin, isolate behind interfaces, monitor advisories, have alternatives | Dev |
| R13 | Fast-moving dependencies break (LiteLLM 5k+ open issues, assistant-ui pre-1.0) | Medium | Medium | Live GitHub data | Pin versions, adapter layer, upgrade tests | Dev |
| R14 | Roman Urdu detection inaccurate | High | Medium | No detector found that lists Roman Urdu (INFERRED) | Custom heuristic + LLM fallback + test corpus | Dev |
| R15 | Free hosting sleeps/pauses/expires | High | Medium | Free tiers not verified (INFERRED from typical plans) | Verify in Phase 1/14; document limits; keep migration kit | Owner |
| R16 | Continuation summaries lose details | Medium | Medium | Spec acknowledges | Keep originals, link provenance, retrieve originals on demand | Dev |
| R17 | Leftover PostgreSQL 18 data directory | Low | Low | `C:\Program Files\PostgreSQL\18\data`, no binaries | Owner decides; new install uses a new data dir | Owner |
| R18 | Project folder under Downloads | Medium | Medium | Path | Move before `git init` | Owner |
| R19 | Missing legal docs (privacy policy, terms, AURA license) | High | High | Not in package | Draft in Phase 14; choose AURA license in Phase 1 | Owner |
| R20 | Secrets committed to GitHub | Low | High | No repo yet; `.gitignore` good | Secret scanning, push protection, pre-commit hook | Dev |
| R21 | Animation cost on low-end devices | Medium | Medium | i3 iGPU, Three.js/GSAP | Lazy-load, Reduced/Off modes, performance budget | Dev |
| R22 | Spec conflicts unresolved (C1–C6) | Medium | Medium | Existing project audit §6 | Owner decisions before Phase 2 | Owner |
| R23 | Web search has no free unlimited option | High | Medium | (INFERRED) | Search adapter; SearXNG self-host (AGPL) or free-tier API with caps | Owner |
| R24 | Object storage not chosen; app disk is ephemeral on many hosts | Medium | High | Spec §Storage | Choose S3-compatible storage with free tier (verify) in Phase 1 | Owner |
| R25 | 50–100 accounts ≠ concurrency estimate | Medium | Medium | Spec notes this | Load test in Phase 14 | Dev |
