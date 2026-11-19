# PHASE 0 — Security Review

- **Date:** 2026-11-20
- **Scope:** Review of the security specification (`docs/08_SECURITY_PRIVACY_ABUSE.md` and related rules), the existing config files, the local environment, and the shortlisted dependencies. There is no code to scan yet, so no vulnerability scan was run.

## 1. Current state of the project folder (VERIFIED)

| Check | Result |
|---|---|
| Real secrets in files | None found. `configs/.env.example` contains placeholders only (`replace_with_a_long_random_secret`, empty keys). |
| `.env` files present | None |
| `.gitignore` | Covers `.env`, `.env.*` (except example), virtualenvs, caches, `node_modules`, builds, logs, SQLite/DB files, `uploads/`, `user_data/`, `private_storage/`, `secrets/` |
| Safe defaults | `ALLOW_PAID_PROVIDER_USAGE=false`, `GLOBAL_DAILY_SPEND_LIMIT=0`, 20 requests/day, 20 MB uploads, 2 concurrent jobs |
| Git repository | None yet, so nothing has been published |

**Gaps in `.gitignore` to add in Phase 2:** `*.pem`, `*.key`, `*.p12`, `.vercel/`, `.idea/`, `.vscode/` (optional), `*.dump`, `*.sql.gz`, `src-tauri/target/`, `.uv-cache/`, `*.env.local` is already covered by `.env.*`.

## 2. Assessment of the security specification

The specification is strong and covers: deny-by-default authorization, IDOR tests, email verification, admin MFA, single-use expiring reset tokens, magic-byte file validation, archive/XML/decompression bomb defenses, prompt-injection separation of instructions from content, approval for side-effecting tools, sandboxed code execution or none, secrets in host secret managers, encrypted provider credentials, per-user and global quotas, zero paid spend by default, data export/deletion, and separate staging.

### Gaps to add to the spec

| ID | Gap | Recommendation |
|---|---|---|
| S1 | No CSRF strategy stated | If cookie sessions are used: SameSite=Lax/Strict + CSRF token; if bearer tokens: store safely, never in `localStorage` for long-lived refresh tokens (INFERRED best practice) |
| S2 | No CORS policy | Explicit allowlist of the frontend origin(s); no `*` with credentials |
| S3 | No security headers | CSP (important with LLM-rendered markdown), HSTS, X-Content-Type-Options, Referrer-Policy, frame-ancestors |
| S4 | LLM output rendering (XSS) | Sanitize markdown/HTML from models; never `dangerouslySetInnerHTML` raw output; sandbox any rendered artifacts |
| S5 | SSRF in research fetcher and MCP | Block private/link-local IP ranges, metadata endpoints, `file://`; resolve-then-connect checks; size and time limits |
| S6 | Bring-your-own API keys | Encrypt at rest (envelope encryption, key outside DB); show only last 4 chars; per-key usage caps |
| S7 | MCP server trust | Only allowlisted MCP servers in public beta; no user-supplied arbitrary MCP command execution on the server |
| S8 | Account enumeration | Uniform responses on signup/login/reset |
| S9 | Audit log integrity | Append-only audit table; admins cannot edit their own audit events |
| S10 | Dependency supply chain | Lockfiles, `pip-audit`, `npm audit`, Dependabot or Renovate, no blind `postinstall` scripts (spec mentions some of this) |
| S11 | Secret scanning tool not named | gitleaks or GitHub secret scanning + push protection (verify license/availability) |
| S12 | Backup encryption | Backups contain user data and must be encrypted and access-controlled |
| S13 | Data residency / provider disclosure UI | Per-provider disclosure before first use, as spec requires; define the copy |
| S14 | Abuse of free AI quotas by bots | CAPTCHA or proof-of-work on signup (choose a privacy-friendly option), email verification before any model call |

## 3. Dependency license and security notes

| Dependency | Concern |
|---|---|
| PyMuPDF (AGPL-3.0) | Avoid in a network service; use pypdf |
| SearXNG (AGPL-3.0) | Only as separate unmodified service; legal review |
| n8n, Open WebUI, LobeHub | Non-permissive or branding-restricted licenses; do not adopt |
| GSAP | Proprietary no-charge license; review terms |
| LiteLLM | Exclude `enterprise/` directory; very high issue volume, pin versions and review upgrades |
| fastapi-users | Maintenance mode |
| python-pptx / openpyxl | Slow maintenance; parse **untrusted** uploads only in an isolated worker with size/time limits; use `defusedxml` protections for OOXML (INFERRED: OOXML is zipped XML, so zip-bomb and XML-entity defenses apply) |
| browser-use / OpenHands | Large attack surface (autonomous browsing/code); out of initial scope |

Per-package advisory lookups (GitHub Advisory Database / OSV) were **not** performed in Phase 0; they are a Phase 1 task.

## 4. Local environment security observations

| Observation | Risk | Action |
|---|---|---|
| Python 3.14 global site-packages has 291 packages incl. torch, transformers | Dependency confusion and version conflicts if AURA uses the global interpreter | Use an isolated `uv` environment only |
| Leftover `C:\Program Files\PostgreSQL\18\data` (74 MB) without binaries | May contain old database files; unknown contents | Owner decides whether to keep; do not reuse blindly |
| Project lives under `Downloads` | Accidental deletion; synced/backup tools may skip or include it unexpectedly | Move to a dev folder before `git init` (owner approval) |
| GitHub CLI absent | None now | Install only if needed, authenticate with least scopes |
| Global npm package `omniroute` present | Unknown relation to AURA | Not used by AURA; owner may review |

## 5. Public beta threat summary (top risks)

1. **Cost exhaustion** through free signups calling model APIs. Mitigation: verified email before use, per-user daily caps, global cap, no paid fallback.
2. **Cross-tenant data leaks** (chats, memory, files). Mitigation: owner filter in every repository method + automated IDOR tests per endpoint.
3. **Prompt injection** from researched pages and uploaded documents leading to tool misuse. Mitigation: tool allowlists, approval gates, no side-effecting tools in beta.
4. **Malicious uploads** (zip bombs, malformed PDFs/OOXML). Mitigation: magic-byte checks, limits, isolated worker, timeouts.
5. **Arbitrary code execution** via Coding Lab. Mitigation: execution disabled until a sandbox is proven.
6. **SSRF** via research fetcher. Mitigation: S5.
7. **Secret leaks** to GitHub. Mitigation: `.gitignore`, secret scanning, push protection.

No claim of security is made for code that does not yet exist. A specialist review is recommended before public launch, as `09_TESTING_QA_ACCEPTANCE.md` already notes.
