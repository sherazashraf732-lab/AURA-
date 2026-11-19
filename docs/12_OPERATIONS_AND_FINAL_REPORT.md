# 12 — Operations, Documentation and Final Report

## Operational requirements
- Health/readiness endpoints.
- Structured logs with request/task IDs.
- Error monitoring.
- Queue depth and worker health.
- Database connection/pool monitoring.
- Provider latency, failure and quota monitoring.
- Usage and storage dashboards.
- Alerts for unusual costs or abuse.
- Backup status and restore evidence.
- Admin audit events.

## Documentation to maintain
- Root README and quick start.
- Architecture overview and decisions.
- Environment setup for Windows and Linux.
- Database/migration guide.
- API docs.
- Module user guides.
- Provider configuration guide.
- Open-source attribution register.
- Security policy and vulnerability reporting.
- Deployment and rollback runbook.
- Backup/restore and migration runbook.
- Troubleshooting guide.
- Known limitations.

## Final completion report
Claude must produce `FINAL_COMPLETION_REPORT.md` containing:

1. Product summary.
2. Implemented modules and exact status.
3. Deployed URLs (only verified URLs).
4. GitHub repository URL (only if created and pushed).
5. Desktop installer path/version (only if actually built).
6. Architecture and technology versions.
7. Open-source projects reused, versions, licenses and attribution.
8. Database migrations and backup/restore evidence.
9. Test summary with command names and pass/fail counts.
10. Security checks and unresolved risks.
11. Performance/load test results and tested concurrency.
12. Known bugs and limitations.
13. Features not implemented.
14. Paid services/credentials still required.
15. How to run locally on another computer.
16. How to deploy/update/rollback.
17. Recommended next actions.

Never claim 100% complete without evidence. If deployment is blocked by account verification, secrets or free-tier limits, clearly mark it BLOCKED and provide exact user action.
