# 09 — Testing, QA and Acceptance Criteria

## Required testing layers

### Backend
- Unit tests for domain services and validators.
- API integration tests.
- PostgreSQL integration tests using disposable test DB.
- Auth/RBAC and cross-tenant isolation tests.
- Migration upgrade tests.
- Provider adapter contract tests using mocks.
- Background job retry/cancel/checkpoint tests.
- File parser security and size-limit tests.

### Frontend
- Component tests for important controls.
- Route and state tests.
- Form validation tests.
- Accessibility checks.
- Responsive layout checks.
- Visual regression/screenshot review for key screens.
- Reduced-motion tests.
- No dead buttons or fake loading states.

### End-to-end
Use Playwright or another selected maintained browser automation tool:
1. Visitor opens landing page.
2. User signs up and verifies account (test mail provider).
3. User signs in.
4. User creates workspace/project.
5. User chats in selected language.
6. Memory controls operate.
7. Long conversation continuation summary is created and resumed.
8. User uploads permitted file.
9. Research flow produces cited output using deterministic test fixtures.
10. User exports document.
11. User checks usage.
12. Admin reviews test user and suspends test account.
13. User cannot access another user's records.
14. User can export/delete their data according to policy.

### Security
- Dependency vulnerability scan.
- Secret scan.
- Static analysis.
- Authorization/IDOR tests.
- Prompt injection tests for retrieved content.
- Upload/parser abuse tests.
- Rate limit and quota tests.
- Sandbox escape review by design; do not claim security without specialist review.

### Performance/reliability
- Load test representative endpoints and job queues.
- Test slow provider, provider timeout and provider quota exhaustion.
- Test DB unavailable, object storage unavailable and worker restart.
- Verify backups and restore in a separate environment.
- Monitor memory and CPU.

## Definition of Done per feature
- Requirements met.
- Open-source review recorded.
- UI complete in approved design system.
- API/service complete.
- Auth/permissions applied.
- Loading/empty/error/success states present.
- Unit/integration/E2E tests appropriate to risk.
- Documentation updated.
- No unresolved critical/high severity defect.
- Known limitations disclosed.

## Release gates
Do not launch public beta until:
- Auth and email verification work.
- User data isolation tests pass.
- Secret scanning passes.
- Rate limits and quotas are active.
- File limits and safe parsing are active.
- Paid provider usage is disabled by default.
- Privacy/terms and deletion policy are available.
- Error monitoring and admin controls work.
- Backup and restore procedure is tested.
- Production smoke tests pass.

## Final status categories
- PASS: verified with evidence.
- PARTIAL: works with documented limits.
- BLOCKED: external dependency/credential/hosting issue.
- NOT TESTED: no evidence; never imply it works.
