# PHASE 1 — Owner Decisions (PENDING)

- **Date:** 2026-11-20
- **Status:** All seven decisions below are **PENDING OWNER APPROVAL**. Nothing here is final until Sammer answers. Research and ADR drafting continue in parallel, using the recommended option as a working assumption and marked as such.
- **How to answer:** reply with one line per decision, e.g. `C1: A, C2: A, C3: B, C4: A, C5: A, C6: A, L: A`. "Other" with your own wording is always fine.

---

## C1 — Browser automation scope

**Conflict:** The Phase 0 brief lists "browser automation" and "Browser and MCP integrations" as AURA capabilities. `docs/01_PRODUCT_BLUEPRINT.md` says a browser agent is a future candidate only.

| Option | What it means | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | Now: server-side read-only web fetching for research (HTTP fetch + text extraction) and MCP integrations. Later: an interactive browser agent (clicks, forms) as a post-beta feature. | Keeps approved scope; far less prompt-injection and abuse risk; no headless Chromium per user on cheap hosting | No "agent browses for you" feature in beta |
| B | Add a sandboxed interactive browser agent (e.g., browser-use + Playwright) to the beta scope | Matches "browser automation" literally | Each session runs a real Chromium (hundreds of MB RAM, INFERRED); high abuse/injection risk; free hosts unlikely to support it; adds weeks |
| C | Only MCP integrations, no web fetching at all | Smallest | Breaks AI Research (M01) which needs web sources |

**Recommendation: A.** It satisfies research and MCP needs safely and keeps the door open for B after beta.

---

## C2 — When GitHub research happens

**Conflict:** The Phase 0 brief asked for GitHub research in Phase 0; `docs/11_PHASED_EXECUTION_PLAN.md` puts it in Phase 1.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | Treat Phase 0 as the first-pass shortlist and Phase 1 as the deep review (source, tests, advisories, scorecards, register). Update doc 11 wording later to say so. | Matches what actually happened; no repeated work | Needs a one-line doc note in Phase 2 |
| B | Leave doc 11 as is and ignore the overlap | No doc change | Docs stay inconsistent |

**Recommendation: A.**

---

## C3 — When to create the status files

**Conflict:** `CLAUDE_MASTER_INSTRUCTIONS.md` §A.6 says create `BUILD_STATUS.md`, `DECISIONS.md`, `OPEN_SOURCE_REGISTER.md`, `TEST_REPORT.md`, `KNOWN_ISSUES.md` at the start. The Phase 0 brief limited output to eight reports.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| A | Create all five now in Phase 1 at the project root | Satisfies master instructions now | `TEST_REPORT.md` would be empty (no code) |
| **B (recommended)** | Create `OPEN_SOURCE_REGISTER.md`, `DECISIONS.md`, `BUILD_STATUS.md`, `KNOWN_ISSUES.md` now as drafts inside `PHASE_1/`; create `TEST_REPORT.md` in Phase 2 when there is something to test; move the drafts to the repo root when the repo is created in Phase 2 | Nothing written to the root before the repo exists; no empty reports | Files move once in Phase 2 |
| C | Wait until Phase 2 for all five | Simplest | Register and decisions are Phase 1 deliverables in doc 11 |

**Recommendation: B.**

---

## C4 — How far Claude may continue without stopping

**Conflict:** `CLAUDE_KICKOFF_PROMPT.md` says Claude "may continue through safe implementation phases when authorized"; the Phase 0 and Phase 1 briefs say stop after each phase.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | Phase gate: stop after every phase for your explicit approval (current practice). Record it in `DECISIONS.md` as the standing rule. | Full control; matches your instructions | Slower |
| B | Stop only before risky steps (installs, accounts, paid usage, pushes, deploys, destructive changes); continue through safe coding phases | Faster | Less review between phases |

**Recommendation: A** for now. You can switch to B later, e.g., once the foundation (Phases 2–4) is reviewed.

---

## C5 — Audio Intelligence and Computer Vision vs. "voice/video future only"

**Conflict:** M09 Audio Intelligence and M10 Computer Vision are core modules, but the blueprint lists voice and video intelligence as future candidates.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | M09 = uploaded audio files: transcription and analysis. M10 = still images: description, OCR handoff, metadata. Live voice chat and video analysis remain future. | Keeps all 20 core modules; avoids real-time streaming infrastructure | No live voice conversation in beta |
| B | Include live voice conversation (speech in/out) in M09 now | Richer UX | Real-time audio, extra providers, cost; weeks of work |
| C | Move M09/M10 to future entirely | Smaller scope | Drops two approved core modules (you asked to keep all features) |

**Recommendation: A.**

---

## C6 — Evaluation Lab (M20) vs. Evaluation Center (A05)

**Conflict:** Their descriptions nearly duplicate each other.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | One shared evaluation engine and data model. **Evaluation Lab (M20)** = admin/developer side: regression suites, release gates, prompt/model versions. **Evaluation Center (A05)** = user side: run evaluations on their own consented datasets and see reports. | No duplicate code; both features kept and clearly different | Requires clear role permissions |
| B | Merge into a single module and drop one name | Simplest | Removes an approved feature name |
| C | Build two independent modules | Literal reading | Duplicate code and maintenance |

**Recommendation: A.**

---

## L — License for AURA itself

AURA's own code needs a license before any GitHub repository is created. Third-party components keep their own licenses regardless. Options:

| Option | What others may do with AURA's code | Pros | Cons |
|---|---|---|---|
| **A (recommended for now)** **Proprietary, "All rights reserved", private GitHub repo** | Nothing without your permission | Keeps every option open (you can open-source later; you cannot easily un-open-source); protects the product while it is unproven; compatible with all shortlisted dependencies | Not "open source"; outside contributors need explicit permission |
| B **Apache-2.0** (public) | Use, modify, sell, including in closed products; must keep notices; includes an explicit patent grant | Business-friendly, widely trusted, attracts contributors | Competitors can host a copy of AURA without sharing changes |
| C **MIT** (public) | Same as B, shorter, no explicit patent grant | Simplest permissive license | Same competitor exposure as B; weaker patent protection |
| D **AGPL-3.0** (public) | Use and modify, but anyone who runs a modified AURA as a network service must publish their source | Strong protection against closed SaaS clones | Discourages business adoption; if you ever want to sell closed licenses you need all contributors' copyright (CLA) |
| E **Source-available** (e.g., Functional Source License / Business Source License, converts to Apache/MIT after ~2–4 years) | Read and self-host for non-competing use; commercial competing use forbidden until conversion | Public code with protection against clones | Not OSI open source; some developers avoid it |

**Recommendation: A** during development and the 50–100 tester beta. Revisit before or after public launch; if you then want open source, B (Apache-2.0) is the usual choice, or D/E if blocking hosted clones matters.

**Dependency compatibility note (VERIFIED from license texts read in Phase 0/1):** All shortlisted dependencies are compatible with every option above. **GSAP:** the formal license text grants use for any website or web app and prohibits only use in no-code visual animation builders that compete with Webflow. AURA is not such a tool. However, the same page still shows an older "plain English summary" saying the free license applies only when end users are not charged. If AURA ever charges users, get written confirmation from GSAP/Webflow or use Motion only. Recorded as risk R11 (updated).

---

## Second round (added after free-tier verification, 2026-11-20)

Evidence: `PHASE_1_FREE_TIER_VERIFICATION.md`. Hosting, object storage and sandbox are deferred (ADR-013, ADR-014) and need no answer now.

### D-AI — How beta testers' AI usage is paid for

**Finding:** No verified free tier is both large enough for 50–100 testers and safe for their personal data. Gemini's free tier is the largest, but Google may use the content and human reviewers may read it, personal information must not be sent, and EEA/UK/Swiss users cannot be served. OpenRouter free models allow 50 requests/day in total. Cerebras is a 30-day $5 trial.

| Option | Meaning | Pros | Cons |
|---|---|---|---|
| **A (recommended)** | Free tiers (Gemini + Groq + OpenRouter free) for development and the closed beta, with a mandatory tester consent screen explaining the provider's data use, a per-user daily cap, a global cap, and no EEA/UK/Swiss testers on Gemini free | $0; honest disclosure | Small daily allowance per tester; testers must accept provider data use |
| B | Bring-your-own-key: each tester adds their own free-tier key | Quota and consent are theirs; scales | Friction; key storage security (encrypted, ADR-017) |
| C | Small paid budget with a hard monthly cap that you set | Privacy-safe paid-tier terms; reliable | Costs money; needs your explicit approval and a cap |

Recommendation: **A, with B available as an optional setting.** C only if you approve a budget.

### D-AUTH — Authentication approach

| Option | Pros | Cons |
|---|---|---|
| **A (recommended)** Self-built on FastAPI (argon2 passwords, server-side sessions, email via Resend free: 100/day, 3,000/month) | One database; no pausing; full control of isolation | More security code to own and test |
| B fastapi-users | Faster start | Maintenance mode |
| C Supabase Auth (50,000 MAU free) | Email, OAuth, MFA handled | Free project pauses after 1 week inactivity; ties AURA to Supabase |

Recommendation: **A.**

### D-SEARCH — Web search provider for AI Research

| Option | Pros | Cons |
|---|---|---|
| **A (recommended)** Tavily free (1,000 credits/month, no card) behind a swappable interface | No card; built for LLM research | ~1,000 searches/month shared by all testers |
| B Brave Search ($5 free credits/month) | Independent index | **Card required**; results may not be stored |
| C Self-hosted SearXNG | No API quota | AGPL; needs a server; engines may block it |

| D Exa free ($10 credit resetting monthly ≈ 2,500 Lite searches, no card; VERIFIED 2026-11-20, added from the awesome-free-ai-tools review) | ≈2.5× Tavily's free volume; no card | Privacy/terms not yet verified |
| E Tavily + Exa together behind the interface | Most free volume; failover between providers | Two accounts to manage |

Recommendation (updated): **E**, with per-user daily search caps; **A** alone if you prefer one account.
