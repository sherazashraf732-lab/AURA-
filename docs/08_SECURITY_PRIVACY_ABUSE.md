# 08 — Security, Privacy and Public Beta Abuse Controls

## Threat model
AURA is a public multi-user AI service. Assume malicious uploads, prompt injection in web pages/documents, credential theft attempts, abusive automation, cost exhaustion, cross-tenant access attempts and unsafe third-party tools.

## Authentication and account protection
- Email verification for public signup.
- Secure password hashing if local passwords are used; prefer established auth provider integration when appropriate.
- Secure session handling, refresh-token rotation and logout/revocation.
- Admin MFA.
- Login/signup rate limits and bot protection.
- Password reset tokens must expire and be single-use.

## Authorization and tenant isolation
- Deny by default.
- Enforce user/workspace/project ownership server-side.
- Test IDOR and cross-user access.
- Admin endpoints require explicit roles.
- Do not trust frontend role or owner IDs.

## File security
- Limit file size, count and types.
- Validate actual content/magic bytes, not extension alone.
- Store uploads outside executable web roots.
- Scan or safely parse untrusted files.
- Protect against archive bombs, malformed PDFs, XML entity expansion and decompression bombs.
- Use isolated workers and time/resource limits.
- Do not expose direct public object URLs for private files.

## AI and prompt-injection security
- Treat retrieved pages, documents, tool outputs and user files as untrusted data.
- Separate instructions from content.
- Tool calls must use allowlisted schemas and permission scopes.
- Require human approval for external side effects, sending messages, publishing, purchases, destructive actions or sharing.
- Do not let a document or webpage override system/security rules.
- Validate model-generated structured output before execution.

## Code execution
- Never run user code in the FastAPI process or host shell.
- Use isolated containers/sandboxes with no default network, restricted filesystem, CPU/memory/time limits and non-root user.
- Do not mount secrets or host home directories.
- Add cleanup and abuse monitoring.
- If safe sandbox infrastructure is not available, disable execution and provide code-only assistance.

## Secrets and configuration
- `.env` ignored by Git.
- `.env.example` contains placeholders only.
- Use hosting secret manager in production.
- Encrypt sensitive provider credentials; keep encryption keys separate.
- Rotate credentials and document incident response.
- Never print keys in logs or final reports.

## Cost and resource controls
- Per-user and global request quotas.
- Token and file-processing budgets.
- Concurrency limits.
- Provider timeouts and backoff.
- Hard cap on paid spend; default paid spend is zero until user approval.
- Queue limits and cancellation.
- Admin alerts for unusual usage.

## Privacy
- Explain what data is sent to each external AI provider.
- Offer provider/data controls where possible.
- Provide data export and account deletion.
- Publish retention and backup deletion policy.
- Collect minimum necessary telemetry.
- Do not use private user data for model training/evaluation without explicit consent.

## Public beta
- Open registration is allowed, but protected by verification, rate limits and quotas.
- Start with conservative resource caps.
- Load-test expected concurrency; 50–100 accounts is not equivalent to 50–100 simultaneous users.
- Provide abuse reporting and admin suspension.
- Keep staging separate from production.
