# PHASE 0 — Environment Audit

- **Date:** 2026-11-20
- **Machine:** DESKTOP-859FMNM
- **Method:** Read-only commands only (`Get-CimInstance`, `Get-Command`, `--version` flags, `pip list`, `npm ls -g`, `Test-Path`). Nothing was installed, changed or started.
- **Legend:** VERIFIED = observed by command output on this machine. INFERRED = reasoning, not directly observed.

## 1. Operating system and hardware (VERIFIED)

| Item | Value |
|---|---|
| OS | Microsoft Windows 11 Pro Education, 64-bit |
| Version / build | 10.0.26300 / 26300 |
| CPU | 12th Gen Intel Core i3-1215U, 6 cores / 8 threads |
| RAM | 7.64 GB total, **0.76 GB free** at time of check |
| Disk C: | 237.5 GB total, **35.6 GB free** |
| Hypervisor present | Yes (virtualization available to Windows) |
| WebView2 runtime | 157.0.4341.60 (needed later by Tauri) |

**Assessment:** This is a low-resource laptop for this project. 8 GB RAM with under 1 GB free matches the warning in `CLAUDE_MASTER_INSTRUCTIONS.md` §I. Local LLMs, Docker Desktop plus PostgreSQL plus a dev server plus a browser test run at the same time will likely exhaust memory (INFERRED). 35.6 GB free disk is enough for development but not generous once Docker images, `node_modules` and Python environments accumulate.

## 2. Development tools

| Tool | Status | Version / path |
|---|---|---|
| Git | VERIFIED installed | 2.55.0.windows.4 (global user.name is set) |
| GitHub CLI (`gh`) | **NOT FOUND** | — |
| Node.js | VERIFIED | v24.19.0 via nvm-windows (`C:\nvm4w`); v26.7.0 also installed in nvm |
| npm | VERIFIED | 11.17.0 |
| corepack | VERIFIED | 0.35.0 (can enable pnpm without a separate install, INFERRED) |
| pnpm / yarn / bun | NOT FOUND | — |
| Python (default) | VERIFIED | **3.14.6** |
| Python 3.12 | VERIFIED | also installed (`py -0p`) |
| pip | VERIFIED | 26.2.2 (for 3.14) |
| uv | VERIFIED | 0.13.6 |
| poetry / pipx | NOT FOUND | — |
| VS Code | VERIFIED | 1.144.0 |
| winget | VERIFIED | v1.29.380 |
| FFmpeg | VERIFIED | 9.0.2 (winget package) |
| Playwright browsers | VERIFIED present | `%LOCALAPPDATA%\ms-playwright` has chromium-1248 (the Python `playwright` package itself is not installed) |
| Docker | **NOT FOUND** (no `docker` command, no `C:\Program Files\Docker`) |
| WSL | **NOT INSTALLED** (`wsl.exe` says the subsystem is not installed) |
| Rust / cargo / rustup | **NOT FOUND** (required for Tauri later) |
| Visual Studio Build Tools | NOT FOUND (`vswhere.exe` absent; required for Tauri/Rust on Windows later) |
| Tesseract (OCR) | NOT FOUND |
| Pandoc / LibreOffice | NOT FOUND |
| Java / Go / Deno / make / choco / scoop | NOT FOUND |

## 3. Databases and services

| Item | Status |
|---|---|
| PostgreSQL | **NOT USABLE.** `C:\Program Files\PostgreSQL\18\` exists but contains only a `data` folder (74 MB). No `bin\psql.exe`, no `postgres` Windows service. This looks like a leftover data directory from an uninstalled PostgreSQL 18 (INFERRED). Do not delete it without the owner's decision; it may contain old data. |
| Redis | NOT FOUND |
| MySQL / MongoDB | No services found |
| Any SQL-like Windows service | None |

## 4. Existing global dependencies

**npm global packages (VERIFIED):** `@anthropic-ai/claude-code@2.1.308`, `corepack@0.35.0`, `npm@11.17.0`, `omniroute` (registry shows 3.8.54, MIT, `cheaper-inference/OmniRoute`). Omniroute is unrelated to the AURA spec; it is noted only so it is not confused with a project dependency.

**Python 3.14 global site-packages (VERIFIED):** 291 packages, installed globally (no project virtualenv). Relevant ones:

| Present | Version |
|---|---|
| pydantic | 2.13.5 |
| pydantic-settings | 2.16.0 |
| starlette | 1.6.0 |
| uvicorn | 0.52.4 |
| httpx | 0.28.1 |
| tenacity | 9.1.4 |
| psycopg | 3.3.6 |
| argon2-cffi | 25.1.0 |
| cryptography | 50.0.2 |
| langchain-core | 1.6.6 |
| groq | 1.7.0 |
| chromadb | 1.5.9 |
| sentence-transformers | 6.1.0 |
| torch | 2.14.1 |
| transformers | 5.19.0 |
| spacy | 3.8.16 |
| argostranslate | 1.11.0 |
| pandas | 3.0.5 |
| numpy | 2.5.2 |
| openpyxl | 3.1.5 |
| pypdf | 6.21.0 |
| beautifulsoup4 | 4.15.0 |

**Not installed globally:** fastapi, sqlalchemy, alembic, langgraph, asyncpg, python-docx, python-pptx, polars, playwright (Python), pytest, ruff, mypy, mcp, PyJWT, structlog, trafilatura, lingua.

**Assessment:** The global Python already carries heavy ML packages (torch, transformers, sentence-transformers). AURA must **not** use the global interpreter; Phase 2 should create an isolated `uv` project environment so AURA's lockfile is the single source of truth.

## 5. Project folder and Git status (VERIFIED)

- Folder: `C:\Users\Hp\Downloads\AURA_CLAUDE_MASTER_BUILD_PACKAGE\AURA_CLAUDE_MASTER_BUILD_PACKAGE`
- **Not a Git repository** (`fatal: not a git repository`).
- No `package.json`, `pyproject.toml`, lockfile, `node_modules` or virtualenv exist in the folder.
- Location is inside `Downloads` and nested twice with the same name (INFERRED risk: easy to delete by accident; consider moving to e.g. `C:\dev\aura` in Phase 2 with owner approval).

## 6. Claude Code tooling available in this session (VERIFIED from session configuration)

- Shell: PowerShell 5.1 and Git Bash.
- Built-in browser pane and Claude in Chrome tools are available for research and later E2E checks.
- The GitHub MCP connector is configured but **requires sign-in**; it was not used. GitHub facts in this phase came from the public GitHub REST API (unauthenticated) and raw license files.
- Vercel, Figma, Notion, Linear and Google connectors are present but were not used (not needed for Phase 0).

## 7. Compatibility notes

| Topic | Note |
|---|---|
| Python 3.14 | Very new. Most core libraries list `>=3.10/3.11`, but compiled packages (e.g., some ML or PDF libs) may lag on 3.14 wheels (INFERRED). **Recommend Python 3.12 or 3.13 for AURA via `uv`** (3.12 is already installed). |
| Node 24 | Current LTS line; compatible with Vite 8 / React 19 / Tailwind 4 per their stated engine ranges (INFERRED, confirm at Phase 2). |
| PostgreSQL | Needed from Phase 4. Options: native PostgreSQL 17/18 Windows installer, Docker (not installed, heavy on 8 GB), or a free hosted dev database. |
| Tauri | Needs Rust toolchain + MSVC Build Tools (both missing) + WebView2 (present). Only needed in Phase 16. |

## 8. Missing items, by phase where they are first needed

| Needed by | Item | Notes |
|---|---|---|
| Phase 2 | GitHub CLI `gh` (optional but recommended) | for repo creation/PRs; or use web UI |
| Phase 2 | pnpm (via corepack) | only if pnpm is chosen as the JS package manager |
| Phase 2 | Project virtualenv via `uv` (uv already present) | Python 3.12/3.13 |
| Phase 4 | PostgreSQL server + `psql` | native install recommended on this RAM budget |
| Phase 8+ | Redis (optional) | avoidable if a PostgreSQL-backed queue is chosen |
| Phase 12 | Docker or another sandbox | needed for safe code execution; without it Coding Lab must stay code-only |
| Phase 13 | Tesseract (OCR) | only when OCR module starts |
| Phase 16 | Rust (rustup), MSVC Build Tools | Tauri desktop |

Nothing above has been installed. Each install needs owner approval.
