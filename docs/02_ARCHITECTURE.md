# 02 — Technical Architecture

## Architecture style
Start with a **modular monolith** and background worker process(es). Extract services only when measurable scaling or isolation requirements justify it.

## Logical components

### Frontend
- React + TypeScript + Vite.
- Tailwind CSS and selected shadcn/ui components.
- Shared design tokens and component library.
- Framer Motion for route, panel, card, modal and state transitions.
- GSAP only for complex choreographed sequences.
- Three.js only for limited hero/branding scenes; provide reduced-motion and low-power alternatives.
- TanStack Query or equivalent for server state, after evaluating current project fit.
- React Router or equivalent routing.
- Form validation with a maintained schema library.

### Backend
- Python + FastAPI.
- Pydantic request/response schemas and settings.
- SQLAlchemy 2.x + Alembic.
- PostgreSQL production.
- Async database driver selected after compatibility testing.
- Provider adapters, domain services and repositories.
- Background worker/queue for research, file ingestion, exports and automation.
- WebSocket or Server-Sent Events for live task/agent progress where useful.

### Storage
- PostgreSQL for relational metadata and task state.
- Persistent object storage for user uploads and generated outputs.
- Optional vector database only when semantic retrieval is justified.
- Start with keyword/BM25 retrieval and modular retrieval interfaces; add embeddings/vector DB after evaluation.
- Cache only where measurable benefit exists.

### AI orchestration
- Supervisor coordinates bounded workflows.
- Agent tools have explicit schemas and permissions.
- Checkpoints, cancellation, deadlines, retries and budgets are mandatory.
- Model adapters expose a common interface.
- Keep provider-specific request/response handling out of domain logic.

### Desktop
- Tauri is preferred candidate after a small technical proof.
- Reuse the web UI and backend API.
- Local file access must require user action/permissions.
- Never expose backend secrets in desktop bundle.
- Windows first; other OS support later.

## Suggested repository structure

```text
aura/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── SECURITY.md
├── CHANGELOG.md
├── BUILD_STATUS.md
├── DECISIONS.md
├── OPEN_SOURCE_REGISTER.md
├── TEST_REPORT.md
├── KNOWN_ISSUES.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pyproject.toml
├── uv.lock                         # or one chosen lockfile, not multiple competing locks
├── package.json
├── pnpm-lock.yaml                  # if pnpm is selected
├── apps/
│   ├── web/
│   │   ├── src/
│   │   │   ├── app/
│   │   │   ├── routes/
│   │   │   ├── layouts/
│   │   │   ├── components/
│   │   │   ├── design-system/
│   │   │   ├── features/
│   │   │   │   ├── auth/
│   │   │   │   ├── chat/
│   │   │   │   ├── research/
│   │   │   │   ├── agents/
│   │   │   │   ├── documents/
│   │   │   │   ├── data-studio/
│   │   │   │   ├── coding-lab/
│   │   │   │   ├── workflows/
│   │   │   │   ├── knowledge/
│   │   │   │   ├── admin/
│   │   │   │   └── settings/
│   │   │   ├── hooks/
│   │   │   ├── lib/
│   │   │   ├── services/
│   │   │   ├── state/
│   │   │   ├── styles/
│   │   │   └── tests/
│   │   └── public/
│   └── desktop/
│       ├── src/
│       └── src-tauri/
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   └── dependencies/
│   │   ├── core/
│   │   ├── auth/
│   │   ├── database/
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── repositories/
│   │   ├── services/
│   │   ├── modules/
│   │   │   ├── chat/
│   │   │   ├── memory/
│   │   │   ├── research/
│   │   │   ├── fact_check/
│   │   │   ├── agents/
│   │   │   ├── model_router/
│   │   │   ├── knowledge_base/
│   │   │   ├── documents/
│   │   │   ├── data_studio/
│   │   │   ├── coding_lab/
│   │   │   ├── workflows/
│   │   │   ├── automation/
│   │   │   ├── mcp_hub/
│   │   │   ├── knowledge_graph/
│   │   │   ├── ocr/
│   │   │   ├── audio/
│   │   │   ├── vision/
│   │   │   ├── workspace/
│   │   │   ├── admin/
│   │   │   ├── usage/
│   │   │   ├── security/
│   │   │   └── evaluation/
│   │   ├── providers/
│   │   ├── workers/
│   │   ├── events/
│   │   └── utils/
│   ├── migrations/
│   └── tests/
├── packages/
│   ├── shared-types/
│   ├── api-client/
│   └── design-tokens/
├── infra/
│   ├── docker/
│   ├── deployment/
│   ├── monitoring/
│   └── scripts/
├── docs/
│   ├── architecture/
│   ├── api/
│   ├── operations/
│   └── user-guide/
├── scripts/
└── .github/
    └── workflows/
```

Claude may adjust this structure if it documents why. Do not create empty folders for every future idea; add module directories when implementation begins.

## Dependency policy
Maintain one authoritative dependency strategy per ecosystem. Pin compatible versions and commit lockfiles. Run dependency audit. Optional heavy dependencies must be isolated behind extras or module-specific requirements.

## Suggested Python dependency categories

Core candidates (verify current versions and compatibility):
- fastapi, uvicorn
- pydantic, pydantic-settings
- sqlalchemy, alembic
- psycopg (or compatible async PostgreSQL driver)
- httpx, tenacity
- python-multipart
- structlog or standard structured logging
- pytest, pytest-asyncio, coverage
- ruff, mypy (or selected type checker)

Feature-specific candidates:
- langgraph for agent orchestration after comparison
- provider SDKs only for enabled providers
- trafilatura / beautifulsoup4 / lxml for web extraction
- pymupdf / pypdf for PDF handling
- python-docx, python-pptx, openpyxl for office files
- pandas / polars / numpy for data analysis
- rank-bm25 for keyword retrieval
- sentence-transformers / qdrant-client / chromadb only after evaluation
- Pillow for image processing
- pytesseract or OCR engine only when OCR is implemented
- networkx for knowledge graph prototypes

Security/testing candidates:
- argon2-cffi or maintained password hashing integration if local passwords are used
- PyJWT or maintained auth provider SDK
- cryptography
- slowapi or gateway-level rate limiting
- defusedxml
- pip-audit, bandit
- respx for HTTP client tests
- Playwright for browser E2E tests

Do not install all candidates at once. Use existing maintained integrations where possible. Confirm each library's license, maintenance and compatibility.
