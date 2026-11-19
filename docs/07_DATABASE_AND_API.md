# 07 — PostgreSQL Database and API Design

## Database rules
- PostgreSQL is the production database.
- Use SQLAlchemy models and Alembic migrations.
- UUID primary keys are recommended for externally exposed records.
- Store UTC timestamps; convert for display.
- Add indexes for common owner/project/time queries.
- Enforce ownership/tenant filters in repositories and services.
- Consider PostgreSQL Row-Level Security only with careful tests and documented connection/session behavior; application authorization remains mandatory.
- Avoid storing large binary files directly in relational rows unless justified; use object storage and metadata records.
- Use soft-delete only where product policy requires it; document actual deletion and backup retention.

## Core entities (initial conceptual schema)
- users
- user_profiles
- workspaces
- workspace_members
- projects
- project_instructions
- conversations
- conversation_messages
- conversation_summaries
- user_memories
- project_memories
- files
- file_versions
- generated_artifacts
- tasks
- task_events
- agent_runs
- agent_steps
- model_providers
- user_provider_credentials (encrypted/secret references; never plaintext)
- model_catalog
- usage_events
- quotas
- workflows
- workflow_versions
- workflow_runs
- knowledge_sources
- document_chunks
- citations
- evaluation_datasets
- evaluation_runs
- audit_events
- feature_flags
- notifications

Claude must refine entities, relationships, constraints and indexes before migrations. Do not create a huge speculative schema for modules not yet implemented.

## API conventions
- Version APIs under `/api/v1`.
- Use consistent JSON response/error schemas.
- Validate all inputs with Pydantic.
- Use pagination for list endpoints.
- Enforce auth, ownership, RBAC and quotas at service boundaries.
- Use idempotency keys for sensitive/retryable creation operations where appropriate.
- Provide OpenAPI docs.
- Use request IDs and structured logs.
- Never include secrets in errors or logs.

## Example route groups
- `/auth/*`
- `/users/me`
- `/workspaces/*`
- `/projects/*`
- `/conversations/*`
- `/memory/*`
- `/research/*`
- `/agents/*`
- `/models/*`
- `/files/*`
- `/documents/*`
- `/data/*`
- `/workflows/*`
- `/usage/*`
- `/admin/*`
- `/evaluations/*`

## Background tasks
Long research, ingestion, conversion and workflow operations should be asynchronous jobs. Track states such as queued, running, waiting_for_approval, succeeded, failed, cancelled. Provide event history and cancellation semantics.

## Realtime
Use SSE or WebSocket only where justified for live agent/task status. Reconnect behavior, authorization, heartbeat and event ordering must be tested.
