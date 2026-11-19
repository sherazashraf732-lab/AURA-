# Open Source Register (DRAFT — candidates, nothing integrated yet)

- **Format:** `configs/OPEN_SOURCE_REGISTER_TEMPLATE.md`, condensed into one row per component. Each row becomes a full template entry when the component is actually integrated.
- **Review date:** 2026-11-20. **Reviewer:** Claude (Phase 1), pending owner approval.
- **Fields still empty by design:** exact commit pinned, tests performed, modifications — filled at integration time.

| Component | Repository / package | License (inspected) | Notice / reciprocal obligations | What AURA would reuse | Alternatives compared | Security / maintenance (2026-11-20) | Status |
|---|---|---|---|---|---|---|---|
| React | github.com/facebook/react · npm `react` 19.3.1 | MIT | Keep license notice in bundle | UI library | — | 0 current advisories; very active | Approved (spec) |
| Vite | github.com/vitejs/vite · `vite` 8.3.8 | MIT | Notice | Build/dev server | — | 29 historical, 0 current; dev server not exposed | Approved (spec) |
| Tailwind CSS | tailwindlabs/tailwindcss · 4.3.5 | MIT | Notice | Styling | — | 0 advisories | Approved (spec) |
| shadcn/ui | shadcn-ui/ui · CLI 4.23.0 | MIT | Notice in copied components | Component source copied into repo | — | Active | Approved (spec) |
| Motion | motiondivision/motion · `motion` 14.14.0 | MIT | Notice | UI animation | GSAP | 0 advisories | Approved (spec) |
| GSAP | greensock/GSAP · `gsap` 3.15.1 | GSAP Standard "No Charge" License (proprietary) | Must not remove notices; prohibited in Webflow-competing visual builders; summary text mentions charging users | Choreographed sequences only | Motion | 1 old advisory | **Conditional** (owner decision L note) |
| Three.js | mrdoob/three.js · 0.187.0 | MIT | Notice | Hero/startup 3D | CSS/Canvas | 1 old advisory | Approved (spec), limited |
| TanStack Query | TanStack/query · 5.108.1 | MIT | Notice | Server state | SWR | 0 advisories | Proposed |
| assistant-ui | assistant-ui/assistant-ui · `@assistant-ui/react` 0.15.37 | MIT | Notice | Chat primitives | Vercel AI SDK UI, custom | 0 advisories; 2,900 commits/90 d | Proposed (ADR-011) |
| DOMPurify | cure53/DOMPurify (npm `dompurify`) | Apache-2.0 OR MPL-2.0 (verify at integration) | Notice | Sanitize model output | sanitize-html | 33 historical; keep latest | Proposed |
| Recharts | recharts/recharts · 3.11.0 | MIT | Notice | Charts | ECharts | 0 advisories | Proposed (ADR-010) |
| xyflow | xyflow/xyflow · `@xyflow/react` 13.0.2 | MIT | Notice | Workflow editor | — | 0 advisories | Proposed |
| FastAPI | fastapi/fastapi · 0.165.0 | MIT | Notice | API framework | — | 0 current | Approved (spec) |
| SQLAlchemy | sqlalchemy/sqlalchemy · 2.1.9 | MIT | Notice | ORM | — | 0 current | Approved (spec) |
| Alembic | sqlalchemy/alembic · 1.20.1 | MIT | Notice | Migrations | — | 0 advisories | Approved (spec) |
| psycopg 3 | psycopg/psycopg · 3.3.9 | **LGPL-3.0** | Use unmodified as a library; keep license; if modified, publish modifications to psycopg | PostgreSQL driver | asyncpg | 0 advisories | Approved (spec) |
| Pydantic / pydantic-settings | pydantic/pydantic · 2.14.4 | MIT | Notice | Schemas, settings | — | 0 current | Approved (spec) |
| LangGraph (+ checkpoint-postgres) | langchain-ai/langgraph · 1.2.23 | MIT | Notice | Agent graphs, checkpoints | Pydantic AI | 0 current; 275 commits/90 d | Proposed (ADR-002) |
| LiteLLM (library only) | BerriAI/litellm · 1.110.1 | MIT **except `litellm/enterprise/`** | Never import enterprise code | Provider calls behind AURA adapter | Official SDKs, Pydantic AI | 85 historical, 0 current; heavy deps | Proposed (ADR-003) |
| MCP Python SDK | modelcontextprotocol/python-sdk · `mcp` 2.3.0 | MIT | Notice | MCP client | — | 16 historical, 0 current | Proposed |
| procrastinate | procrastinate-org/procrastinate · 3.12.0 | MIT | Notice | Postgres job queue | Celery, ARQ | 0 advisories | Proposed (ADR-005) |
| trafilatura | adbar/trafilatura · 2.3.1 | Apache-2.0 | Keep NOTICE if present | Page text extraction | BeautifulSoup | 0 advisories | Proposed |
| lingua-py | pemistahl/lingua-py · 2.2.0 | Apache-2.0 | Keep NOTICE if present | Language ID | fastText | 0 advisories; quiet since 2026-03 | Proposed (ADR-008) |
| pgvector | pgvector/pgvector | PostgreSQL License | Keep copyright notice | Vector search (stage 2) | Qdrant | Active | Proposed (ADR-006) |
| python-docx | python-openxml/python-docx · 1.2.0 | MIT | Notice | DOCX | — | 0 current; quiet since 2025-06 | Proposed |
| python-pptx | scanny/python-pptx · 1.0.2 | MIT | Notice | PPTX | — | 0 advisories; **idle since 2024-08** | Proposed with risk |
| openpyxl | foss.heptapod.net/openpyxl · 3.1.5 | MIT | Notice | XLSX | — | 0 current; last release 2024-06 | Proposed with risk |
| pypdf | py-pdf/pypdf · 7.1.1 | BSD-3-Clause | Keep copyright notice | PDF reading | PyMuPDF (AGPL, rejected) | 119 historical, 0 current | Proposed (isolated worker) |
| ReportLab | reportlab (PyPI) | BSD (verify at integration) | Notice | PDF writing | WeasyPrint | 8 historical | Proposed (ADR-009) |
| pandas / polars | PyPI 3.0.5 / 2.1.0 | BSD-3 / MIT (verify pandas at integration) | Notice | Data analysis | — | 0 current | Proposed |
| argon2-cffi | PyPI 25.1.0 | MIT (verify at integration) | Notice | Password hashing | bcrypt | 0 advisories | Proposed (ADR-004 option A) |
| slowapi | laurentS/slowapi · 0.1.10 | MIT | Notice | Per-IP throttling | custom middleware | 0 advisories; small test suite | Proposed, secondary |
| Sentry SDK | getsentry/sentry-python · 2.75.0 | MIT | Notice | Error reporting | GlitchTip | 0 current | Proposed |
| Playwright | microsoft/playwright-python · 1.65.2 | Apache-2.0 | Notice | E2E tests | — | 0 advisories | Proposed (tests only) |
| Tauri | tauri-apps/tauri · CLI 2.12.6 | Apache-2.0 / MIT | Notice | Desktop (Phase 16) | Electron | Active | Approved (spec) |

## Rejected / reference only

| Project | Reason |
|---|---|
| n8n | Sustainable Use License, not open source; enterprise files need paid license |
| Open WebUI | License forbids removing its branding above a user threshold |
| LobeHub (lobe-chat) | Community license requires a commercial license for derivative distribution |
| PyMuPDF | AGPL-3.0 network-use obligations |
| open_deep_research | Archived |
| mem0 | Not needed; AURA owns memory tables (ADR-007) |
| fastapi-users | Maintenance mode (ADR-004) |
| OpenHands, browser-use | Out of approved scope / too heavy (C1) |
| SearXNG | AGPL; only as separate service if owner chooses it (ADR-012) |
| Marker / Surya weights | OpenRAIL-M weights, free only under $5M funding/revenue |
| Arize Phoenix | Elastic License 2.0 (not OSI) |
| Activepieces, Langflow, Flowise, Windmill, Dify | Separate platforms duplicating the approved Workflow Engine; Windmill AGPL; Dify forbids multi-tenant use |
| LlamaIndex, Haystack, RAGFlow | Duplicate LangGraph + own retrieval |
| NVIDIA NIM free endpoints | Prototyping only; production needs paid license |

## Added candidates from the awesome-free-ai-tools review (2026-11-20, see `PHASE_1_GITHUB_RESEARCH.md`)

| Component | License (inspected) | Status |
|---|---|---|
| Docling | MIT | Candidate, Phase 9/13 |
| Tesseract / OCRmyPDF | Apache-2.0 / MPL-2.0 | Candidate, Phase 13 |
| faster-whisper | MIT | Candidate, Phase 13 |
| promptfoo | MIT except `/enterprise/` | Candidate, CI evals |
| DeepEval | Apache-2.0 (check `/enterprise/`) | Candidate, Evaluation Lab |
| FastMCP | Apache-2.0 | Candidate, MCP Hub |
