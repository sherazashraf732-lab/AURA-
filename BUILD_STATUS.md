# BUILD STATUS (2026-11-20)

Nothing is deployed or pushed. Local Git only.

| Area | Status | Evidence |
|---|---|---|
| Phase 2 repo foundation | PARTIAL | Lint/type/test pass locally; CI file written, not yet run on GitHub |
| Phase 3 web shell/design system | PARTIAL | 7 web tests pass; build passes (main bundle 560 KB, code-split routes) |
| Phase 4 backend + PostgreSQL | PARTIAL | App core done; project-local PostgreSQL 18.7 downloaded, extraction in progress; Alembic migration not yet generated |
| Phase 5 auth/workspaces | NOT TESTED | Code written; 12 DB tests not yet run |
| Phase 6 model router + chat | NOT TESTED | Code + UI written; 14 DB tests not yet run |
| Phase 7 memory/continuation/language | PARTIAL | Roman Urdu detector: 19 tests pass; memory/summary API + UI not yet DB-tested |
| Phase 8 research/agents | NOT TESTED | SSRF guard + parsers: 13 tests pass; runner/Control Room not yet DB-tested |
| Phases 9–17 | NOT STARTED | — |

Next steps: finish PostgreSQL extraction, run `scripts/dev-db.ps1 start`, run `uv run pytest` and fix failures, generate the initial Alembic migration, then continue Phase 9.
