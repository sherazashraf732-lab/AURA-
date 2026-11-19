# PHASE 0 — Existing Project Audit

- **Date:** 2026-11-20
- **Scope:** Every file in the project folder was read in full. No file was modified, moved or deleted.

## 1. Inventory (VERIFIED)

| # | Path | Bytes | Type | Purpose |
|---|---|---|---|---|
| 1 | `README_FIRST.md` | 2146 | Doc | Reading order and package intent |
| 2 | `CLAUDE_KICKOFF_PROMPT.md` | 2022 | Prompt | Kickoff text to paste into Claude Code |
| 3 | `CLAUDE_MASTER_INSTRUCTIONS.md` | 8968 | Rules | Non-negotiable execution rules (A–K) |
| 4 | `.gitignore` | 269 | Config | Secrets, envs, caches, uploads excluded |
| 5 | `configs/.env.example` | 709 | Config | Placeholder env vars, paid usage off by default |
| 6 | `configs/OPEN_SOURCE_REGISTER_TEMPLATE.md` | 497 | Template | Per-component license register entry |
| 7 | `docs/01_PRODUCT_BLUEPRINT.md` | 2848 | Spec | Vision, roles, journeys, scope (20 + 5), releases A–E |
| 8 | `docs/02_ARCHITECTURE.md` | 7432 | Spec | Modular monolith, repo layout, dependency candidates |
| 9 | `docs/03_OPEN_SOURCE_FIRST_POLICY.md` | 2931 | Policy | Discovery, 10-point scorecard, register rules |
| 10 | `docs/04_UI_UX_ANIMATION_SYSTEM.md` | 3572 | Spec | Visual direction, startup sequence, required screens |
| 11 | `docs/05_MODULE_SPECIFICATIONS.md` | 5808 | Spec | 20 core modules, 5 additions, central assistant |
| 12 | `docs/06_CHAT_MEMORY_LANGUAGE.md` | 3377 | Spec | 3 context layers, continuation flow, language rules |
| 13 | `docs/07_DATABASE_AND_API.md` | 2686 | Spec | Entity list, API conventions, job states |
| 14 | `docs/08_SECURITY_PRIVACY_ABUSE.md` | 3490 | Spec | Threat model, auth, files, prompt injection, sandbox |
| 15 | `docs/09_TESTING_QA_ACCEPTANCE.md` | 3017 | Spec | Test layers, 14-step E2E, release gates |
| 16 | `docs/10_DEPLOYMENT_GITHUB_MIGRATION.md` | 2569 | Spec | CI steps, hosting candidates, migration kit |
| 17 | `docs/11_PHASED_EXECUTION_PLAN.md` | 3796 | Plan | Phases 0–17 and gate template |
| 18 | `docs/12_OPERATIONS_AND_FINAL_REPORT.md` | 1883 | Spec | Ops requirements, final report contents |
| 19 | `specs/ACCEPTANCE_CHECKLIST.md` | 1924 | Checklist | Release acceptance boxes (all unchecked) |
| 20 | `specs/FEATURE_MATRIX.md` | 1719 | Spec | M01–M20, A01–A05 |
| 21 | `specs/aura_manifest.json` | 970 | Spec | Machine-readable scope summary |
| 22 | `templates/FINAL_COMPLETION_REPORT_TEMPLATE.md` | 745 | Template | Final report |
| 23 | `templates/PHASE_REPORT_TEMPLATE.md` | 338 | Template | Phase report |

Only new additions by this phase: the `PHASE_0/` folder and its eight reports.

## 2. Existing code

**None.** No source files, no `package.json`, `pyproject.toml`, lockfiles, migrations, tests, Dockerfiles or CI workflows exist. The package itself says it is "a build specification, not a claim that AURA has already been implemented." The acceptance checklist is entirely unchecked. **Nothing is implemented or tested.**

## 3. Approved decisions to preserve (VERIFIED from docs)

1. Modular monolith + background worker(s); no premature microservices.
2. Frontend: React + TypeScript + Vite, Tailwind CSS, shadcn/ui, Framer Motion; GSAP and Three.js only where justified.
3. Backend: Python + FastAPI, Pydantic, SQLAlchemy 2.x, Alembic, PostgreSQL.
4. Provider-neutral model adapter layer; deterministic mock provider for tests.
5. LangGraph as orchestration candidate, **subject to comparison and a written decision**.
6. Start retrieval with keyword/BM25; vector DB only after evaluation.
7. Web beta first (50–100 testers, open signup with verification), Tauri desktop later.
8. Paid provider usage off by default (`ALLOW_PAID_PROVIDER_USAGE=false`, `GLOBAL_DAILY_SPEND_LIMIT=0`).
9. Scope: exactly 20 core modules + exactly 5 additions (A1–A5). Voice, video, local model hosting, browser agent are future only.
10. Design: deep navy/graphite, electric violet + cyan glow, honest progress indicators, reduced-motion and Full/Reduced/Off animation setting.
11. Code execution only in an isolated sandbox; otherwise disabled.
12. Hosting candidates (not commitments): Vercel (frontend), Render (API/worker), Supabase (DB/auth/storage).

## 4. Approved modules (VERIFIED)

Core: M01 AI Research, M02 Fact Checker, M03 AI Agents, M04 Model Router, M05 Knowledge Base/RAG, M06 Document Studio, M07 Data Studio, M08 OCR, M09 Audio, M10 Computer Vision, M11 Coding Lab, M12 Workflow Engine, M13 Automation, M14 Plugin/MCP Hub, M15 Knowledge Graph, M16 User Workspace, M17 Admin Dashboard, M18 Usage Manager, M19 Security Center, M20 Evaluation Lab.

Additions: A01 Universal Workspace + Project Continuity, A02 Memory Intelligence, A03 Live Agent Control Room, A04 Model Arena, A05 Evaluation Center.

## 5. Coverage of the 15 capabilities in the Phase 0 brief

| # | Capability | Covered in specs? | Where | Gap |
|---|---|---|---|---|
| 1 | Advanced AI conversations | Yes | 06, M04 | — |
| 2 | Multiple model providers | Yes | M04, .env.example | Free-tier terms not yet verified (deferred to Phase 6 by design) |
| 3 | Deep research with sources | Yes | M01, M02 | Search provider not chosen |
| 4 | Agents / multi-agent | Yes | M03, A03 | — |
| 5 | Coding and project development | Partly | M11 | Sandbox technology undecided; "coding agent" (autonomous repo edits) not specified |
| 6 | File upload and document analysis | Yes | M05, 08 | — |
| 7 | Editable PPTX/DOCX/XLSX | Yes | M06 | PDF generation library not chosen |
| 8 | Data analysis + visualization | Yes | M07 | Chart library not chosen |
| 9 | Browser and MCP integrations | **Conflict** | M14 covers MCP; blueprint lists "browser agent" as **future only** | See C1 |
| 10 | Workflow automation | Yes | M12, M13 | Visual editor library not chosen |
| 11 | Persistent user memory | Yes | A02, 06 | — |
| 12 | History and search | Yes | 06 | Search technique (Postgres FTS?) not stated |
| 13 | Multilingual | Partly | 06 | **Roman Urdu not explicitly named** (see M2) |
| 14 | Settings and personalization | Yes | 04 screens, M19 | — |
| 15 | Secure auth and accounts | Yes | 08, Phase 5 | Build vs. hosted auth undecided |

## 6. Conflicts (need owner decision)

| ID | Conflict | Evidence | Recommendation |
|---|---|---|---|
| C1 | Browser automation | Phase 0 brief lists "browser automation" and "Browser and MCP integrations"; `01_PRODUCT_BLUEPRINT.md` says browser agent is a future candidate only | Keep the approved scope: allow read-only web fetch for research now; treat an interactive browser agent as future, unless the owner promotes it |
| C2 | When GitHub research happens | Phase 0 brief asks for GitHub research now; `11_PHASED_EXECUTION_PLAN.md` puts it in Phase 1 | This phase did a first-pass shortlist; Phase 1 should deepen it (source inspection, scorecards, `OPEN_SOURCE_REGISTER.md`, ADRs) |
| C3 | Status files | `CLAUDE_MASTER_INSTRUCTIONS.md` A.6 says create `BUILD_STATUS.md`, `DECISIONS.md`, `OPEN_SOURCE_REGISTER.md`, `TEST_REPORT.md`, `KNOWN_ISSUES.md` at the start; Phase 0 brief restricts output to eight reports | Not created now. Create them at the start of Phase 1 or 2 after approval |
| C4 | Kickoff vs. Phase 0 brief | `CLAUDE_KICKOFF_PROMPT.md` says "continue through safe implementation phases when authorized"; Phase 0 brief says stop and wait | Phase 0 brief wins (most recent owner instruction). Stopped after Phase 0 |
| C5 | Audio Intelligence / Computer Vision vs. "voice, video intelligence future only" | M09/M10 are core; blueprint lists voice and video intelligence as future | Interpret M09 as file-based transcription, M10 as still images; real-time voice and video are future. Confirm with owner |
| C6 | Evaluation Lab (M20) vs. Evaluation Center (A05) | Near-identical descriptions | Build as one module with two faces (internal regression lab + user-facing center), or confirm they are distinct |

## 7. Duplications

- M20 Evaluation Lab ≈ A05 Evaluation Center (see C6).
- M16 User Workspace overlaps A01 Universal Workspace + Project Continuity (A01 extends M16; fine if treated as one domain).
- M12 Workflow Engine and M13 Automation overlap (one engine, scheduling as a trigger type is the natural reading, INFERRED).

## 8. Missing or underspecified requirements

| ID | Missing item |
|---|---|
| M1 | No **LICENSE** decision for AURA itself (needed before public GitHub repo). Required in `02_ARCHITECTURE.md` repo layout but not chosen. |
| M2 | **Roman Urdu** detection is not explicitly specified; most language detectors classify Roman Urdu as English or Hindi (INFERRED from how script-based detectors work). Needs a custom heuristic or LLM-based classification plus tests. |
| M3 | No **web search provider** chosen for research (free options have strict quotas; self-hosted SearXNG is AGPL). |
| M4 | No **email provider** for verification/reset emails (needed in Phase 5). |
| M5 | No **object storage** provider chosen. |
| M6 | No **auth approach** decision: self-built on FastAPI vs. hosted (Supabase Auth etc.). |
| M7 | No **job queue** decision (Redis-based vs. PostgreSQL-based). |
| M8 | No **sandbox** decision for Coding Lab. |
| M9 | No **context-window threshold** numbers or summary schema version for continuation. |
| M10 | No **data retention period** or deletion SLA. |
| M11 | No **Privacy Policy / Terms of Service** content (release gate requires them). |
| M12 | No **admin bootstrap** procedure (how the first admin is created, MFA method). |
| M13 | No **quota numbers** beyond `.env.example` defaults (20 requests/day, 20 MB uploads, 2 concurrent jobs). |
| M14 | No **i18n of the UI** stated (only conversation language); RTL is "where possible". |
| M15 | No **accessibility target level** (e.g., WCAG 2.2 AA). |
| M16 | No **monitoring provider** (Sentry or alternative) chosen. |
| M17 | No **domain name** decision for the public beta. |

## 9. Quality of the package

The specification is coherent, safety-conscious and realistic about verification. It intentionally leaves concrete library and provider choices to research. The main weaknesses are breadth (25 modules for a solo developer on an 8 GB laptop) and the unresolved items in §6 and §8.
