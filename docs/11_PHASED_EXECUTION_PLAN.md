# 11 — Phased Execution Plan

Claude must work sequentially. Do not skip acceptance gates.

## Phase 0 — Environment and project assessment
Inspect machine, tools, repo, runtimes, storage, network and current state. Create status and decision logs. Do not install blindly.

## Phase 1 — Open-source discovery and architecture validation
Research candidates for UI, auth, AI orchestration, chat, RAG, document/data handling, workflow, observability and desktop. Compare alternatives and licenses. Produce `OPEN_SOURCE_REGISTER.md` and architecture decision records.

## Phase 2 — Repository foundation
Set up Git, monorepo structure, linting, formatting, type checks, CI, env templates and basic docs. Verify clean build.

## Phase 3 — Design system and animated frontend shell
Implement brand, startup sequence, responsive navigation, dashboard, settings, reusable components, accessibility and reduced-motion mode. Build actual navigation and working states, not static screenshots.

## Phase 4 — Backend and PostgreSQL foundation
FastAPI app, config, database session, SQLAlchemy models, Alembic, health endpoint, structured errors, logging, test database and migrations.

## Phase 5 — Authentication and workspaces
Signup, verification, login, sessions, password reset, workspace/project ownership, authorization and user isolation tests.

## Phase 6 — Model Router and central chat
Provider adapters, model catalog, user-selected provider configuration, streaming, usage tracking, quotas, deterministic mock provider, no silent paid fallback.

## Phase 7 — Memory and conversation continuity
Durable memory, project memory, chat summaries, context threshold logic, continuation chat, language detection, manual override and privacy controls.

## Phase 8 — Research and agent system
Research planner, search/source adapters, evidence analysis, citation provenance, supervisor, bounded agents, checkpoints and live Agent Control Room.

## Phase 9 — Fact Checker and Knowledge Base
Claim verification, ingestion, chunking, BM25 retrieval, citations, access control. Add vector search only after evaluation.

## Phase 10 — Document Studio
DOCX/PDF/PPTX/XLSX creation, templates, editing/export flows and file validation tests.

## Phase 11 — Data Studio
CSV/XLSX import, schema inspection, cleaning, statistics, charts, export, sandbox/resource limits.

## Phase 12 — Coding Lab and workflow automation
Code assistance; safe sandbox only if isolation can be demonstrated. Workflow definitions, execution, approvals, logs and MCP permissions.

## Phase 13 — Remaining core modules
OCR, audio, vision, knowledge graph, plugin/MCP hub, usage manager, security center and Evaluation Lab. Implement only with verified dependencies and safe limits.

## Phase 14 — Public beta hardening
Admin dashboard, anti-abuse controls, rate limits, monitoring, backups, privacy documentation, load/security testing and staging rehearsal.

## Phase 15 — Public web beta
Deploy frontend, API, workers, database and object storage. Configure open registration with protective controls. Run production smoke tests. Publish known limitations.

## Phase 16 — Desktop application
Tauri proof, shared frontend/API, local file permissions, Windows packaging and update/release testing.

## Phase 17 — Final audit and handover
Full test run, dependency/license audit, backup restore, migration rehearsal, documentation review and final evidence-based report.

## Phase gate report template
- Phase:
- Work completed:
- Files/modules changed:
- Open-source projects integrated:
- License/attribution status:
- Commands run:
- Tests passed/failed:
- Bugs found and fixed:
- Remaining defects:
- Security/performance risks:
- User action needed:
- Decision to proceed: yes/no with reason.
