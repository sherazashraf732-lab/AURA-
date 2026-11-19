# PHASE 1 — Deep Technical Research

- **Date:** 2026-11-20
- **Methods (all read-only, nothing installed or executed):**
  1. **Security advisories:** OSV.dev API (aggregates GitHub Advisory DB, PyPA, npm) queried for each package, both all-time and for the exact latest version.
  2. **Source, tests, CI:** bare, blob-less `git clone` of each repo into a scratch folder (no checkout, no scripts run); commit history since 2026-08-20 (90 days), file tree for tests/workflows/SECURITY.md, and selected source files read on demand.
  3. **Licenses:** license files read directly (Phase 0) plus the GSAP license page (Phase 1).
- **Limits:** Test-file counts are by filename pattern and indicate presence, not coverage. CI pass/fail status was not read (GitHub API rate limit was exhausted). Advisory counts are historical; "affecting current" is what matters.

## 1. Security advisories (OSV, 2026-11-20)

**Result: no known advisory affects the latest version of any shortlisted package.**

| Package | Ecosystem | Latest | All-time advisories | Affecting latest | Most recent advisory | Reading |
|---|---|---|---|---|---|---|
| fastapi | PyPI | 0.165.0 | 3 | 0 | 2024-02 | Low |
| starlette | PyPI | 1.6.0 | 20 | 0 | 2026-07 | Keep current (FastAPI's base) |
| sqlalchemy | PyPI | 2.1.9 | 6 | 0 | 2022 | Low |
| alembic | PyPI | 1.20.1 | 0 | 0 | — | Low |
| psycopg | PyPI | 3.3.9 | 0 | 0 | — | Low |
| pydantic | PyPI | 2.14.4 | 4 | 0 | 2026-07 | Low |
| langgraph | PyPI | 1.2.23 | 4 | 0 | 2026-10-28 | Medium; pin and watch |
| langchain-core | PyPI | 1.6.6 | 18 | 0 | 2026-07 | Medium; transitive via LangGraph |
| **litellm** | PyPI | 1.110.1 | **85** | 0 | 2026-10-27 | **High churn**; mostly proxy-server issues (INFERRED from volume); library-only use, pin exact |
| pydantic-ai | PyPI | 2.71.0 | 28 | 0 | 2026-10-15 | Medium |
| mcp | PyPI | 2.3.0 | 16 | 0 | 2026-10-27 | Medium; MCP is a young protocol |
| mem0ai | PyPI | 2.2.1 | 10 | 0 | 2026-10-28 | Not adopted (ADR-007) |
| bm25s | PyPI | 0.3.16 | 0 | 0 | — | Low |
| trafilatura | PyPI | 2.3.1 | 0 | 0 | — | Low |
| playwright | PyPI | 1.65.2 | 0 | 0 | — | Low |
| browser-use | PyPI | 1.0.6 | 2 | 0 | 2026-06 | Out of scope (C1) |
| lingua-language-detector | PyPI | 2.2.0 | 0 | 0 | — | Low |
| python-docx | PyPI | 1.2.0 | 2 | 0 | 2022 | Low |
| python-pptx | PyPI | 1.0.2 | 0 | 0 | — | Low (but unmaintained) |
| openpyxl | PyPI | 3.1.5 | 2 | 0 | 2022 | Low |
| **pypdf** | PyPI | 7.1.1 | **119** | 0 | 2026-10-30 | Parser for untrusted PDFs; isolate + resource limits + always latest |
| polars / pandas | PyPI | 2.1.0 / 3.0.5 | 0 / 1 | 0 | — | Low |
| procrastinate | PyPI | 3.12.0 | 0 | 0 | — | Low |
| fastapi-users | PyPI | 15.0.5 | 2 | 0 | 2026-07 | Maintenance mode |
| slowapi | PyPI | 0.1.10 | 0 | 0 | — | Low |
| sentry-sdk | PyPI | 2.75.0 | 4 | 0 | 2026-07 | Low |
| argon2-cffi | PyPI | 25.1.0 | 0 | 0 | — | Low |
| uvicorn / httpx | PyPI | 0.52.4 / 0.28.1 | 4 / 2 | 0 | 2020 / 2022 | Low |
| python-multipart | PyPI | — | 18 | (latest not queried) | 2026-07 | FastAPI form/upload dependency; keep latest |
| pyjwt | PyPI | — | 48 | (n/a) | 2026-10 | Avoided by ADR-004 (server-side sessions) |
| reportlab | PyPI | — | 8 | (n/a) | 2026-07 | Proposed PDF writer; check latest at install |
| weasyprint | PyPI | — | 10 | (n/a) | 2026-10 | Not proposed |
| defusedxml | PyPI | — | 0 | — | — | Use for any XML parsing |
| react | npm | 19.3.1 | 2 | 0 | 2020 | Low |
| **vite** | npm | 8.3.8 | 29 | 0 | 2026-10-29 | Dev-server issues; never expose dev server publicly |
| tailwindcss / motion | npm | 4.3.5 / 14.14.0 | 0 / 0 | 0 | — | Low |
| gsap / three | npm | 3.15.1 / 0.187.0 | 1 / 1 | 0 | 2021 | Low |
| @tanstack/react-query | npm | 5.108.1 | 0 | 0 | — | Low |
| @assistant-ui/react | npm | 0.15.37 | 0 | 0 | — | Low |
| ai (Vercel) | npm | 7.0.177 | 1 | 0 | 2025-11 | Not proposed |
| @xyflow/react / recharts | npm | 13.0.2 / 3.11.0 | 0 / 0 | 0 | — | Low |
| echarts | npm | 6.1.0 | 1 | 0 | 2026-05 | Low |
| @modelcontextprotocol/sdk | npm | 1.32.2 | 9 | 0 | 2026-10-27 | Only if needed client-side |
| react-router | npm | — | 20 | (n/a) | 2026-07 | Keep latest |
| **dompurify** | npm | — | 33 | (n/a) | 2026-10-22 | Needed for sanitizing model output; must stay on latest |
| @tauri-apps/cli / tauri crate | npm / crates | 2.12.6 / — | 1 / 9 | 0 / n/a | 2026-05 | Phase 16 |

**Policy derived:** packages with high advisory volume (litellm, pypdf, dompurify, vite, langchain-core, mcp) are acceptable but must be pinned, scanned in CI (`pip-audit`, `npm audit`/OSV-Scanner) and upgraded on advisory.

## 2. Maintenance, tests and CI (git history, VERIFIED)

| Repo | Commits since 2026-08-20 | Distinct authors (90 d) | Last commit | CI workflow files | Test files (pattern) | SECURITY.md |
|---|---|---|---|---|---|---|
| langchain-ai/langgraph | 275 | 26 | 2026-11-19 | 17 | 242 | not found at root |
| BerriAI/litellm | (history too large to clone in time) | — | 2026-11-19 | 41 | 7,821 | yes |
| pydantic/pydantic-ai | (not measured, timeout) | — | 2026-11-19 | 59 | 3,881 | no |
| assistant-ui/assistant-ui | 2,900 | 101 | 2026-11-19 | 31 | 2,093 | yes |
| procrastinate-org/procrastinate | 162 | 16 | 2026-11-19 | 4 | 89 | no |
| modelcontextprotocol/python-sdk | 77 | 6 | 2026-11-05 | 10 | 287 | yes |
| adbar/trafilatura | 136 | 59 | 2026-11-18 | 2 | 1,046 | no |
| xhluca/bm25s | 17 | 9 | 2026-11-13 | 5 | 47 | no |
| py-pdf/pypdf | 353 | 78 | 2026-11-19 | 9 | 49 | yes |
| pemistahl/lingua-py | 0 | — | **2026-03-09** | 1 | 0 detected (Rust-backed; tests may live in the Rust crate, INFERRED) | no |
| scanny/python-pptx | 0 | — | **2024-08-07** | 1 | 185 | no |
| python-openxml/python-docx | 0 | — | **2025-06-16** | 0 | 127 | no |
| fastapi-users/fastapi-users | 0 | — | 2026-08-17 | 3 | 21 | yes |
| laurentS/slowapi | 0 | — | **2026-06-13** | 1 | 4 | no |

**Readings:**
- Core orchestration, chat UI, queue, MCP, extraction and PDF libraries are actively maintained with real test suites.
- **python-pptx (27 months idle), python-docx (17 months idle), lingua (8 months idle), slowapi (5 months idle, only 4 test files)** are stable-but-quiet. All have no open advisories. They are acceptable behind interfaces; slowapi is small enough that AURA's DB-backed quotas should be the primary limiter, with slowapi (or an equivalent middleware) only for per-IP request throttling.

## 3. Source-code findings (read on demand, VERIFIED)

| Repo | File inspected | Finding | Impact |
|---|---|---|---|
| litellm | `litellm/__init__.py` | `success_callback = []`, `failure_callback = []`, `turn_off_message_logging = False` by default | No external logging callbacks are enabled by default; AURA must set `turn_off_message_logging=True` so prompts never go to any logger it later adds |
| litellm | `pyproject.toml` | Core dependencies include `openai`, `tokenizers`, `huggingface-hub`, `boto3`, `aiohttp`, `jinja2`, `tiktoken`, `jsonschema` | **Heavy footprint** even for library use. Accept for development; reconsider official SDKs if install size or advisories become a problem (ADR-003 fallback) |
| procrastinate | `pyproject.toml` | Depends on `psycopg[pool]`; optional `alembic` extra | Same driver as AURA (psycopg 3) and Alembic integration available — good fit |
| langgraph | repo tree `libs/` | `checkpoint-postgres`, `checkpoint-sqlite`, `checkpoint-conformance` present | Postgres checkpoints are first-party |
| lingua-py | `README.md` | Supports **Urdu** and Hindi; **no Roman Urdu** | Confirms ADR-008 custom Roman Urdu layer is required |

## 4. Scorecards (spec `03_OPEN_SOURCE_FIRST_POLICY.md`, 0–5 each)

Criteria: L license, S security, M maintenance, D docs, T tests/CI, F dependency footprint, A architecture fit, P performance, I i18n/a11y, E ease of extracting only needed parts. D and P are partly INFERRED.

| Component | L | S | M | D | T | F | A | P | I | E | Total /50 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| LangGraph | 5 | 4 | 5 | 4 | 4 | 3 | 5 | 4 | 3 | 4 | **41** |
| Pydantic AI | 5 | 4 | 5 | 4 | 5 | 4 | 4 | 4 | 3 | 4 | **42** |
| LiteLLM (library) | 4 | 3 | 5 | 4 | 5 | 2 | 5 | 4 | 3 | 3 | **38** |
| assistant-ui | 5 | 4 | 5 | 4 | 5 | 4 | 5 | 4 | 3 | 4 | **43** |
| procrastinate | 5 | 5 | 4 | 4 | 4 | 5 | 5 | 3 | 3 | 5 | **43** |
| MCP Python SDK | 5 | 3 | 4 | 4 | 4 | 4 | 5 | 4 | 3 | 4 | **40** |
| trafilatura | 5 | 5 | 4 | 4 | 4 | 4 | 5 | 4 | 4 | 5 | **44** |
| lingua-py | 5 | 5 | 3 | 4 | 3 | 4 | 4 | 5 | 4 | 5 | **42** |
| python-pptx | 5 | 5 | 1 | 4 | 4 | 5 | 5 | 4 | 3 | 5 | **41** |
| pypdf | 5 | 3 | 5 | 4 | 3 | 5 | 5 | 3 | 3 | 5 | **41** |
| Recharts | 5 | 5 | 5 | 4 | 3 | 4 | 5 | 4 | 3 | 4 | **42** |
| xyflow | 5 | 5 | 5 | 5 | 3 | 4 | 5 | 4 | 3 | 4 | **43** |

**Note on LangGraph vs. Pydantic AI:** Pydantic AI scores one point higher overall (lighter, better typing), but LangGraph scores higher on the criterion AURA's spec stresses most (architecture fit for checkpoints and human approval). ADR-002 therefore keeps the approved LangGraph. This is a close call and is flagged for owner awareness; AURA's `AgentRunner` interface keeps either option open.

## 5. Recommended register entries

See `OPEN_SOURCE_REGISTER_DRAFT.md`. Entries are recorded as **candidates**; the "Version/commit" and "Tests performed" fields are completed at integration time (Phase 2+), as the template requires.
