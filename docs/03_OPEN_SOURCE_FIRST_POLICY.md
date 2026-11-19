# 03 — Open-Source-First Policy (Highest Priority)

## Objective
Reduce development time and avoid reinventing reliable components by discovering, evaluating and integrating suitable open-source projects from GitHub and official package ecosystems.

## Discovery sources
- GitHub repository search and topic pages.
- Official documentation and release pages.
- Package registries (PyPI, npm, crates.io).
- Security advisories and vulnerability databases.
- License texts and SPDX identifiers.

## Search categories
Search by capability, not only by product name:
- AI chat UI and conversation management
- research orchestration and web search connectors
- agent graph/orchestration and human approval
- RAG ingestion, chunking, retrieval and citations
- document editor and office export
- spreadsheet/data analysis and charting
- workflow automation and visual node editors
- auth, RBAC, audit logs and tenant isolation
- admin dashboards and usage metering
- MCP client/server integrations
- observability and evaluation frameworks
- Tauri desktop integration

## Candidate scorecard
Score each candidate 0–5:
1. License compatibility.
2. Security posture.
3. Maintenance and release activity.
4. Documentation and examples.
5. Test coverage and CI.
6. Dependency footprint.
7. Architecture compatibility.
8. Performance and scalability.
9. Accessibility/localization.
10. Ease of extracting only needed capability.

Do not choose solely by stars or popularity.

## Required register entry
For every adopted dependency/repository record:
- Name and repository URL.
- Exact version, release or commit.
- License and SPDX identifier if known.
- Copyright/NOTICE requirements.
- What is reused.
- What is modified.
- Why selected over alternatives.
- Security review date and known advisories.
- Dependency/transitive dependency concerns.
- Required source/attribution notices.
- Whether source changes must be published under license terms.
- Upgrade/maintenance owner.

## Integration rules
- Prefer package-level integration over copying source.
- If vendoring is necessary, retain copyright and license notices and isolate vendored code.
- Avoid copying full applications when a library or API is enough.
- Keep AURA's proprietary/custom code clearly separated from third-party code.
- Generate a software bill of materials (SBOM) for release where practical.
- Add automated license/dependency scanning to CI.
- If license is unclear, do not integrate until resolved.
- GPL/AGPL obligations require deliberate legal review, especially for distribution and network use.
- Never remove attribution or license files.
- Never execute an unknown repository's install scripts blindly. Inspect scripts and dependencies first.

## Deliverable
`OPEN_SOURCE_REGISTER.md` must be maintained throughout development. Add a section to each phase report listing reused projects, license findings and custom code that remained necessary.
