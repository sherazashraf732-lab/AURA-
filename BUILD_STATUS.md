# BUILD STATUS (2026-11-20)

Nothing is deployed or pushed. Local Git only.

| Area | Status | Evidence |
|---|---|---|
| Phase 2 repo foundation | PARTIAL | Lint/type/test pass locally; CI file written, not yet run on GitHub |
| Phase 3 web shell/design system | PARTIAL | 7 web tests pass; build passes (main bundle 560 KB, code-split routes) |
| Phase 4 backend + PostgreSQL | PASS (local) | Local PostgreSQL 18.7; initial Alembic migration upgrades/downgrades cleanly, `alembic check` clean |
| Phase 5 auth/workspaces | PASS (backend tests) | 12 tests incl. CSRF, reset, rate limit, enumeration; UI not browser-tested |
| Phase 6 model router + chat | PASS (backend tests, mock provider) | 14 tests incl. cross-user isolation, quota, consent; real providers untested (no keys) |
| Phase 7 memory/continuation/language | PASS (backend tests) | Memory, project memory isolation, summaries, auto-continuation, 19 language tests |
| Phase 8 research/agents | PASS (backend tests, demo sources) | 6 run tests + SSRF guard; real search providers untested (no keys) |
| Phase 9 knowledge base + fact checker | PASS (backend tests) | Upload txt/md/csv/pdf/docx with magic-byte + zip-bomb checks, PostgreSQL full-text search, cited answers, isolation; 6 tests. Only extracted text is stored (no original files yet) |
| Phase 10 document studio | PASS (backend tests) | DOCX/PPTX/XLSX/PDF from one content model, each re-opened to validate; spreadsheet formula-injection guard; AI draft; 8 tests. Known limit: PDF does not render Urdu script; files are not stored |
| Phase 11 data studio | PASS (backend tests) | CSV/XLSX import (50k rows), cleaning, column statistics, grouped chart data, CSV/XLSX export with formula-injection guard, Recharts UI loaded only on that page; 4 tests |
| Phase 12 auto routing, coding lab, workflows | PASS (backend tests, mock + simulated failover) | Auto mode picks a free provider per request and fails over on limits/errors, never to paid or demo; Coding Lab (no execution); workflows with versions, approval steps and run log; 8 new tests. Automation schedules (M13) come in Phase 13 |
| Phase 13 remaining modules | PASS (backend tests + browser smoke) | Security Center, Model Arena, Evaluation Center, automation schedules, OCR/Vision/Audio (Tesseract/Gemini/Groq Whisper/demo, EXIF stripped), allowlisted Integrations with audit, Knowledge Graph with provenance; 12 tests. Browser smoke test (scripts/smoke_e2e.py, Edge): 23/23 pages load with no console errors, chat round trip works. External MCP servers intentionally not offered in beta |
| Phase 14 beta hardening | PASS (local) | 8 free providers in Auto chain; admin dashboard (stats, users, suspend, audit); terms consent + signup honeypot; optional Sentry (no PII) + access logs; backup/restore verified (row counts + migration matched); PRIVACY/TERMS pages, SECURITY.md, DEPLOYMENT.md; browser smoke 25/25 pages. Not done: load test, independent security review, legal review of policy texts |
| Phases 15–17 | NOT STARTED | Phase 15 public deploy needs owner approval |

Backend: 105 tests pass. Web: 7 tests pass. Not yet done: browser end-to-end test of the UI, Phases 9-17.
