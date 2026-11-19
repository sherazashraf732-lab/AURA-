# KNOWN ISSUES (DRAFT)

- **As of:** 2026-11-20. No code yet, so these are planning and environment issues.

| ID | Issue | Severity | Status |
|---|---|---|---|
| K-001 | No free AI tier is both privacy-safe for public users and large enough for 100 testers (Gemini free: data used and human-reviewed, no personal info, no EEA/UK/CH users; OpenRouter free: 50 req/day; Cerebras: 30-day trial) | High | Owner decision D-AI |
| K-002 | Render free tier could not be verified (site unreachable on 2026-11-20) | Medium | Re-verify before choosing API host |
| K-003 | Groq free-tier limits not shown on public docs (only paid Developer limits) | Medium | Read in console after sign-up (owner) |
| K-004 | Vercel Hobby is personal/non-commercial only | Medium | OK for free beta; revisit if AURA charges |
| K-005 | GSAP license summary mentions charging end users; formal terms do not | Low | Owner decision L note |
| K-006 | No PostgreSQL server installed; leftover PG 18 data folder | Medium | Phase 4 install (owner approval) |
| K-007 | 8 GB RAM, under 1 GB free during Phase 0 audit | Medium | Lightweight dev setup (ADR-005, ADR-015) |
| K-008 | python-pptx idle since 2024-08; python-docx since 2025-06; openpyxl last release 2024-06 | Low | Interfaces + file validation |
| K-009 | Roman Urdu not supported by any detector reviewed | Medium | ADR-008 custom layer |
| K-010 | CI pass/fail status of shortlisted repos not checked (API rate limit) | Low | Optional re-check in Phase 2 |
| K-011 | Supabase free projects pause after 1 week inactivity; Neon free scales to zero (cold start) | Low | Factor into hosting choice |
