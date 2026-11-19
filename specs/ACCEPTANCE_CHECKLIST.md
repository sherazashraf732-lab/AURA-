# AURA Release Acceptance Checklist

## Foundation
- [ ] Clean install documented and verified.
- [ ] Git repository and CI checks work.
- [ ] Frontend build passes.
- [ ] Backend starts and health endpoint passes.
- [ ] PostgreSQL migrations upgrade cleanly.
- [ ] Environment secrets are not committed.

## User experience
- [ ] Approved animated visual system is consistent.
- [ ] Startup animation reflects real readiness or clearly indicates indeterminate loading.
- [ ] All main screens responsive.
- [ ] Reduced-motion mode works.
- [ ] Keyboard/accessibility basics pass.
- [ ] No dead controls or fake features.

## Accounts and privacy
- [ ] Open signup with email verification.
- [ ] Auth/session lifecycle tested.
- [ ] User/project isolation tests pass.
- [ ] Memory controls work.
- [ ] Chat continuation summary works and original chat remains available.
- [ ] Export/deletion flows documented and tested.

## AI
- [ ] Provider adapters tested with mocks.
- [ ] No paid provider use without explicit consent.
- [ ] Quota exhaustion does not silently switch to paid.
- [ ] Language matching tests pass.
- [ ] Research citations point to real retrieved sources.
- [ ] Agent cancellation/checkpoint behavior tested.

## Files and output
- [ ] File limits and validation active.
- [ ] Private file access is authorized.
- [ ] Office exports open and validate.
- [ ] Data outputs label units and sources.

## Security and operations
- [ ] Dependency and secret scans pass.
- [ ] Rate limits and quotas active.
- [ ] Code execution disabled unless sandbox verified.
- [ ] Monitoring and admin controls work.
- [ ] Backup and restore test completed.
- [ ] Load test results documented.
- [ ] Production smoke test passes.

## Handover
- [ ] GitHub repo pushed (if authorized).
- [ ] Deployment URL verified.
- [ ] New-computer migration guide tested.
- [ ] Final report lists pass/partial/blocked/not-tested status.
