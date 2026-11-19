# AURA — Claude Code Master Build Package

**Product:** AURA — Your AI Powerhouse  
**Purpose:** A modular, multilingual AI research, intelligence, creation, development and productivity platform.  
**Build approach:** Open-source-first, test-driven, security-conscious, modular monolith first.  
**Release order:** Public web beta first; Windows desktop client after the web foundation is stable.

## Read these files in order

1. `CLAUDE_MASTER_INSTRUCTIONS.md` — non-negotiable execution rules.
2. `docs/01_PRODUCT_BLUEPRINT.md` — product vision and scope.
3. `docs/02_ARCHITECTURE.md` — system architecture and technology choices.
4. `docs/03_OPEN_SOURCE_FIRST_POLICY.md` — GitHub discovery, license and integration process.
5. `docs/04_UI_UX_ANIMATION_SYSTEM.md` — approved visual direction.
6. `docs/05_MODULE_SPECIFICATIONS.md` — all core modules and approved top-five additions.
7. `docs/06_CHAT_MEMORY_LANGUAGE.md` — chat, memory, summaries and multilingual behavior.
8. `docs/07_DATABASE_AND_API.md` — PostgreSQL schema direction and API conventions.
9. `docs/08_SECURITY_PRIVACY_ABUSE.md` — public beta security requirements.
10. `docs/09_TESTING_QA_ACCEPTANCE.md` — mandatory test strategy and release gates.
11. `docs/10_DEPLOYMENT_GITHUB_MIGRATION.md` — GitHub, CI/CD, deployment and portability.
12. `docs/11_PHASED_EXECUTION_PLAN.md` — phase-by-phase build sequence.
13. `docs/12_OPERATIONS_AND_FINAL_REPORT.md` — monitoring, documentation and completion report.
14. `specs/` and `configs/` — machine-readable requirements and templates.

## Important

This package is a build specification, not a claim that AURA has already been implemented. Claude must inspect the actual machine, repository, available tools and current provider plans before choosing exact versions or installing anything.

Do not install every library listed in a broad ecosystem. Discover, justify and install only dependencies needed for the current phase. Keep a lockfile and record why each important dependency exists.

Do not put API keys, passwords, private user data, production database dumps or `.env` files in Git.
