# AURA — Decisions

Authoritative decision log. History: `PHASE_1/PHASE_1_OWNER_DECISIONS.md`, `PHASE_1/PHASE_1_ADRS.md`.

## Authority

On 2026-11-19 the owner (Sammer) delegated engineering decisions and instructed that pending Phase 1 owner decisions be resolved "using the safest recommended options, with any legally or financially significant uncertainty documented for review". Approval boundaries that remain with the owner: spending or paid services, payment details, publishing the repository, public deployment, destructive operations without backup, unclear/incompatible licenses.

## Owner-level decisions (resolved 2026-11-20 under delegation)

| ID | Decision | Choice | Uncertainty flagged for owner review |
|---|---|---|---|
| C1 | Browser automation | Read-only server-side web fetching + MCP now; interactive browser agent after beta | — |
| C2 | Research timing | Phase 0 = shortlist, Phase 1 = deep review | — |
| C3 | Status files | Drafts in `PHASE_1/` kept as history; live files at repo root from Phase 2 | — |
| C4 | Phase gating | **Superseded by owner instruction**: continue through phases autonomously; stop only at approval boundaries, genuine blockers or security concerns | — |
| C5 | Audio / vision | Uploaded audio files and still images; live voice/video future | — |
| C6 | Evaluation Lab vs Center | One engine; Lab = admin regression, Center = user-facing | — |
| L | AURA license | **Proprietary, all rights reserved; private repository** | Revisit before any public release of source |
| D-AI | Beta AI usage | Free tiers only, global + per-user caps, tester consent screen disclosing provider data use, BYOK optional; paid usage disabled | **Legal/privacy:** Gemini unpaid terms allow Google to use and human-review content, forbid personal data, and forbid serving EEA/UK/CH users. AURA will (a) show a provider disclosure and require consent, (b) let users pick a provider, (c) default to providers with no-training statements where available. Owner should review the consent text before public beta |
| D-AUTH | Authentication | Self-built: argon2id passwords, server-side sessions in PostgreSQL, HTTP-only cookies + CSRF token, email verification and reset via pluggable mailer (console mailer in dev; Resend free tier when owner creates an account) | — |
| D-SEARCH | Web search | Tavily + Exa behind `SearchProvider`; per-user daily caps; deterministic fixtures in tests | Provider privacy terms not fully verified |
| GSAP | Animation license | **Not used for now** (Motion + CSS + selective Three.js only). Safest choice because GSAP's page contains a summary restricting free use when end users are charged | Owner may approve GSAP later |

## Engineering decisions (ADRs)

| ID | Decision | Status |
|---|---|---|
| ADR-001 | Modular monolith + worker | Accepted |
| ADR-002 | LangGraph behind `AgentRunner` interface | Accepted |
| ADR-003 | Own `ModelProvider` interface; LiteLLM library (MIT core) + deterministic mock provider | Accepted |
| ADR-004 | Self-built auth (see D-AUTH) | Accepted |
| ADR-005 | procrastinate PostgreSQL job queue | Accepted |
| ADR-006 | Postgres full-text search first, pgvector later | Accepted |
| ADR-007 | Own memory/summaries tables | Accepted |
| ADR-008 | Script detection + lingua + AURA Roman Urdu layer | Accepted |
| ADR-009 | python-docx / python-pptx / openpyxl / pypdf / ReportLab | Accepted |
| ADR-010 | Recharts | Accepted |
| ADR-011 | Chat UI built on shadcn primitives; assistant-ui evaluated at Phase 6 | Accepted |
| ADR-014 | Code execution disabled in beta | Accepted |
| ADR-015 | Python 3.12 + uv; Node 24 + npm | Accepted |
| ADR-016 | Motion first; GSAP not used (see GSAP above) | Accepted |
| ADR-017 | Security baseline (S1–S14) | Accepted |
| ADR-013 | Hosting | Deferred; deployment needs owner approval |

Further decisions are appended below as they are made.

## Log

| Date | ID | Decision |
|---|---|---|
| 2026-11-20 | D-020 | Repository root = the existing package folder (keeps specs and history in one repo); local Git only, no remote until owner approves |
