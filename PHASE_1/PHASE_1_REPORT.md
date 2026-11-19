# PHASE 1 — Report

- **Phase:** 1 — Architecture decisions, conflict resolution and deep technical research
- **Date:** 2026-11-20
- **Decision:** **PARTIAL.** Research and drafts are complete. Ten owner decisions are pending; no decision has been finalized. Phase 2 has not started.

## 1. Work completed

| Item | File |
|---|---|
| Owner decisions C1–C6, license (L), AI usage (D-AI), auth (D-AUTH), search (D-SEARCH), each with options, pros/cons, recommendation | `PHASE_1_OWNER_DECISIONS.md` |
| Security advisories (OSV) for 50+ packages; maintenance, tests and CI from git history; source inspection; scorecards | `PHASE_1_DEEP_RESEARCH.md` |
| Free tiers verified from official pages | `PHASE_1_FREE_TIER_VERIFICATION.md` |
| 18 ADRs (proposed or owner-decision) | `PHASE_1_ADRS.md` |
| Open-source register (candidates + rejected list) | `OPEN_SOURCE_REGISTER_DRAFT.md` |
| Decisions index, build status, known issues | `DECISIONS_DRAFT.md`, `BUILD_STATUS_DRAFT.md`, `KNOWN_ISSUES_DRAFT.md` |

## 2. Files changed

New files only, all in `PHASE_1/`. No existing file was modified, moved or deleted.

## 3. Commands run (all read-only)

- OSV.dev advisory queries (HTTPS API).
- `git clone --bare --filter=blob:none` (history and file trees only, no checkout, no scripts) of 14 repositories into the session scratch folder; `git log`, `git ls-tree`, `git show` to read selected files.
- `curl` of the GSAP license page; WebFetch of official pricing/limits/terms pages.
- Nothing was installed, executed from the downloaded repos, pushed or deployed. No accounts were created and no API keys were used.

## 4. Key findings

1. **Approved architecture stands.** All approved components remain the right choice; no replacement proposed.
2. **No current advisories** affect the latest version of any shortlisted package. High-volume packages (litellm, pypdf, dompurify, vite, langchain-core, mcp) need pinning and CI scanning.
3. **Free AI tiers are the biggest gap.** Gemini free tier allows Google to use and human-review content and forbids personal information and EEA/UK/Swiss users; OpenRouter free is 50 requests/day total; Cerebras is a 30-day trial; Groq's free numbers are not published on its docs page. Quotas are shared by all testers. → decision D-AI.
4. **Hosting terms:** Vercel Hobby is personal/non-commercial only; Supabase free pauses after a week idle; Neon free includes pgvector; Cloudflare R2 has 10 GB free with no egress fees; Render could not be verified.
5. **Roman Urdu:** confirmed unsupported by lingua (which does support Urdu script); ADR-008 defines a custom layer and a test corpus.
6. **LangGraph vs. Pydantic AI** is close (scorecards 41 vs. 42); LangGraph kept for checkpoint and approval fit, behind a replaceable interface.
7. **LiteLLM** has a heavy dependency tree (openai, boto3, huggingface-hub, tokenizers…); acceptable with official-SDK fallback.
8. **Quiet but safe libraries:** python-pptx (idle since 2024-08), python-docx, lingua, slowapi.
9. **GSAP:** formal license allows AURA; its summary text conflicts if AURA ever charges users.

## 5. Owner decisions needed (nothing finalized)

| ID | Topic | Recommended |
|---|---|---|
| C1 | Browser automation scope | A — read-only fetch + MCP now, browser agent later |
| C2 | Research timing | A |
| C3 | Status files | B — drafts in `PHASE_1/`, move at repo creation |
| C4 | Stop after each phase | A |
| C5 | Audio/vision scope | A — files and still images |
| C6 | Evaluation Lab vs. Center | A — shared engine, two faces |
| L | AURA license | A — proprietary, private repo during beta |
| D-AI | Beta AI usage | A — free tiers + consent + caps; BYOK optional |
| D-AUTH | Auth | A — self-built, server-side sessions |
| D-SEARCH | Web search | A — Tavily free behind interface |

## 6. Requirements preserved

Memory Intelligence (ADR-007), Roman Urdu support (ADR-008), public signup with verification and abuse controls (ADR-004, ADR-017), secure multi-user isolation (ADR-017), all 20 core modules and 5 additions, paid usage disabled by default (ADR-003, `.env.example` unchanged).

## 7. Remaining risks

Free-tier volatility and privacy terms (R04/K-001), scope size (R01), low RAM (R02), unverified Render (K-002), Groq free limits unknown (K-003), quiet document libraries (K-008), CI status not checked (K-010).

## 8. User action needed

Answer the ten decisions in §5 (one line is enough, e.g. `C1: A, C2: A, C3: B, C4: A, C5: A, C6: A, L: A, D-AI: A, D-AUTH: A, D-SEARCH: A`). After your answers, Claude will mark the ADRs final and update the drafts. **Phase 2 will not start without your explicit approval.**

## 9. Proposed Phase 2 scope (for your later approval)

Repository foundation only: choose folder location, `git init`, private GitHub repo (if L = A), move the drafts to the root, monorepo skeleton, Python 3.12 uv environment, npm workspace, lint/format/type/test tooling, CI with secret and dependency scanning, `.env.example`, basic docs. Installs needed then: project-local Python and npm dev dependencies only (each listed for approval).
