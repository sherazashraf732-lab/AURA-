# Security

## Reporting a vulnerability
Please do not open a public issue. Contact the repository owner privately via GitHub (profile contact) with steps to reproduce. We aim to respond within 7 days.

## What AURA does today
- Passwords: argon2id. Sessions: random tokens stored only as keyed hashes, HTTP-only SameSite cookies, CSRF double-submit on every state change, sign-out of all sessions on password reset or suspension.
- Account protection: email verification before AI use, uniform responses (no account enumeration), per-IP and per-account rate limits, signup honeypot, admin suspension.
- Isolation: every query filters by owner; cross-user (IDOR) tests cover chats, memory, documents, datasets, workflows, runs and graphs.
- Files: size limits, real-content (magic-byte) checks, zip-bomb and decompression-bomb guards, corrupt files rejected cleanly, images re-encoded (EXIF/GPS removed), only extracted text stored.
- AI safety: retrieved web pages, documents and tool output are treated as data, not instructions; citations are validated; code is never executed; integrations are an allowlist of read-only tools with per-user grants and audit logs; SSRF guard blocks private and metadata addresses.
- Spending: paid providers disabled by default; Auto mode only fails over between free providers; per-user and per-provider daily caps.
- Supply chain: lockfiles; `pip-audit`, `npm audit` and gitleaks in CI; licence register in `THIRD_PARTY_LICENSES.md`.

## Known limits (beta)
- Rate limits and the scheduler are in-process (single API process).
- The SSRF check resolves DNS before connecting (a DNS-rebinding window remains).
- No independent security review has been done yet; one is recommended before a wider launch.
