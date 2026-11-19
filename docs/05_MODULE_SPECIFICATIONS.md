# 05 — Module Specifications

## Core 20 modules

### 1. AI Research
Plan research, search web sources through approved connectors, collect source metadata, extract claims, compare evidence, produce structured reports and citations. Show source URLs, publication dates where available, retrieval timestamps and uncertainty. Do not invent citations.

### 2. Fact Checker
Accept claims or report passages, find supporting/contradicting evidence, label status (supported, contradicted, mixed, insufficient evidence), explain reasoning and cite sources. Avoid binary certainty where evidence is incomplete.

### 3. AI Agents
Agent definitions, tools, permissions, bounded tasks, handoffs, checkpoints, cancellation, retries, budgets and human approval. No unrestricted tool access.

### 4. Model Router
Provider-neutral adapters, model catalog, capability metadata, user selection, task-based routing, fallback rules, latency/usage tracking and explicit paid-provider consent.

### 5. Knowledge Base / RAG
Upload and organize documents, parse, chunk, index, retrieve and cite passages. Start with keyword/BM25 retrieval; evaluate embeddings and vector storage before adding. Enforce per-user/project access isolation.

### 6. Document Studio
Create/edit/export DOCX, PDF, PPTX and XLSX. Separate content model from rendering/templates. Re-open generated files and validate structure. Keep editable outputs where supported.

### 7. Data Studio
Import CSV/XLSX, inspect schema, clean data, calculate descriptive statistics, visualize and export. Use sandboxed, resource-limited data processing. Charts must label units, periods and source data.

### 8. OCR Intelligence
Image/PDF text extraction, confidence indicators and review/correction. Optional heavy engines installed only for this phase. Protect against malformed files and oversized inputs.

### 9. Audio Intelligence
Audio transcription and analysis using supported providers or local libraries after hardware assessment. Enforce upload limits, user consent and provider disclosure.

### 10. Computer Vision
Image classification, OCR handoff, visual question answering and image metadata. Keep models/provider adapters replaceable; no unsupported claims about model accuracy.

### 11. Coding Lab
Code explanation, generation, review, debugging and test assistance. Code execution must run in a restricted sandbox with CPU, memory, time, network and filesystem limits. Never execute arbitrary user code directly in the API process.

### 12. Workflow Engine
Visual or structured workflow definitions, typed nodes, validation, versioning, execution history, checkpoints, retries and human approval steps.

### 13. Automation
Scheduled and event-triggered jobs, task status, pause/cancel, retry policies and audit trails. Default schedules must not create unexpected external side effects.

### 14. Plugin / MCP Hub
Discover, configure and manage integrations. Each tool has declared scopes, schema validation, permission prompts, timeouts and audit logs. Treat tool output as untrusted data.

### 15. Knowledge Graph
Represent entities and relationships extracted from user-approved sources. Show provenance and allow correction. Do not imply uncertain relationships are facts.

### 16. User Workspace
Personal workspaces, projects, chats, files, saved outputs, project instructions and access controls.

### 17. Admin Dashboard
User moderation, service health, feature flags, quotas, provider status, job monitoring and audit events. Enforce role-based access and admin MFA where feasible.

### 18. Usage Manager
Track model/provider usage, requests, storage, task limits and quotas. Prevent surprise paid usage. Show users understandable usage data.

### 19. Security Center
Sessions, connected providers, API keys, data export/deletion, security events, privacy controls and account settings.

### 20. Evaluation Lab
Curated test sets, prompt/model versioning, regression checks, quality metrics, latency, cost and citation evaluation. Do not use private user content in evaluation without explicit consent.

## Only five approved additional features

### A1. Universal Workspace + Project Continuity Engine
Projects group chats, files, instructions, tasks, outputs and memory. Resume long-running work from checkpoints. Maintain a clear project timeline.

### A2. Memory Intelligence
Separate durable user memory, project memory and temporary chat context. Provide user controls to view, edit, disable and delete memory. Use only relevant memories and avoid saving sensitive or temporary details by default.

### A3. Live AI Agent Control Room
Show agent/task name, current step, status, progress when measurable, tool calls, source count, usage, errors and approvals. Allow pause/cancel/retry where safe. Do not expose secrets or private internal reasoning traces; show concise action summaries instead.

### A4. Model Arena
Compare outputs from user-selected models with explicit usage disclosure. Show provider/model, response time, estimated/actual usage and side-by-side responses. Paid models require explicit opt-in. Do not claim objective quality ranking without a defined evaluation.

### A5. Evaluation Center
Run repeatable quality, reliability, latency, cost, citation and regression tests. Track prompt/model versions and release gates. Use synthetic or consented test data.

## Central AURA Assistant
A central assistant is the main entry point. It can route a user request to appropriate modules and agents, but must:
- Explain the planned actions for consequential tasks.
- Ask approval before external side effects, paid usage, sharing or destructive actions.
- Respect user permissions and quotas.
- Provide a unified result with links to created artifacts and task history.
- Avoid claiming a module performed work when it did not.
