# PHASE 1 — GitHub Research Addendum: awesome-free-ai-tools

- **Date:** 2026-11-20
- **Source reviewed:** https://github.com/mdruhulkuddus/awesome-free-ai-tools (README, ~85 KB, 48 sections; list itself is MIT-licensed). Used as a **discovery directory only**. Nothing from it is selected, installed or integrated.
- **Verification method:** Official pricing/docs/terms pages (WebFetch), repository license files and last-commit dates via shallow blob-less `git clone` (no checkout, nothing executed), latest versions from PyPI/npm, advisories from OSV.dev.
- **Legend:** VERIFIED = confirmed on an official page or in the repository. LIST CLAIM = stated only by the awesome list. INFERRED = judgment. NOT VERIFIED = could not confirm.
- **Not collected:** GitHub star counts (API rate limit exhausted; stars are not a selection criterion under the policy).

## 1. Where the list was wrong or out of date (VERIFIED against official sources)

| Item | List says | Official / repository says |
|---|---|---|
| Exa API credits | "API credits are one-time" | **$10 free, resets on the 1st of every month, no payment method required** (exa.ai/pricing) |
| Marker | (implies open source) | Code **Apache-2.0**; model weights **modified OpenRAIL-M: free only for research, personal use and startups under $5M funding/revenue** (repo README, MODEL_LICENSE) |
| Surya | "GPL-3.0 code; free under $2M revenue" | Code now **Apache-2.0**; weights same OpenRAIL-M with **$5M** threshold (repo README) |
| Gemini free tier | "Flash/Flash-Lite only, ~20 RPD reported" | Official rate-limit page shows per-model free limits (one model at 200 RPM / 10,000 RPD); some models not free. Figures differ from the list; trust the official page and your own dashboard |
| n8n | "Open-source" | Sustainable Use License, not OSI open source (Phase 0, license file read) |

**Conclusion:** the list is useful for discovery but its numbers and license labels must not be copied into AURA documents without checking.

## 2. Categories reviewed

**Relevant to AURA (17):** AI research & search; Document & PDF AI; OCR & document extraction; Translation & speech-to-text; Data & spreadsheets; Code review AI; AI-powered dev tools; Developer APIs with free tiers; Local & open-source LLM runners; Notable open-weight models; RAG frameworks; Vector databases; MCP servers & tooling; AI observability & evals; Workflow automation; AI agents; Computer-use agents (scope check only).

**Skipped as outside AURA's approved scope (31):** chatbots (competitors, not components), AI browsers, writing/paraphrasing, productivity apps, meeting notes, presentations/design apps, image/video/3D generation and editing, music/stems, avatars, AI detection/humanizers, resume, study, math, marketing/SEO, website builders, companions, prompt libraries, finance, medical, email AI, voice agents (live voice is future per C5).

## 3. The four buckets

| Bucket | Meaning for AURA | Examples from the list |
|---|---|---|
| **Free web applications** | End-user products. Cannot be embedded in AURA; useful only as UX references or competitors | Perplexity, Gemini Notebook, ChatPDF, Julius AI, Consensus, Elicit, Manus, Genspark |
| **Free APIs (quota-limited)** | Can sit behind AURA's provider/search adapters; quotas are shared by all testers | Groq, Gemini, OpenRouter `:free`, Mistral Experiment, Cloudflare Workers AI, Exa, Tavily, Semantic Scholar |
| **Open-source self-hosted** | Libraries/services AURA could run itself; cost is hardware, not fees | Docling, Tesseract, OCRmyPDF, PaddleOCR, faster-whisper, promptfoo, DeepEval, Opik, FastMCP, Ollama, LanceDB, Activepieces |
| **Limited trials / restricted** | Time-limited, non-production or non-commercial; not suitable as a beta dependency | Cerebras ($5, 30 days), NVIDIA NIM (prototyping only), Cohere trial (non-commercial, LIST CLAIM), Hugging Face ($0.10/month, LIST CLAIM), Brave Search (card required) |

## 4. Shortlisted free APIs (verified)

| Service | Verified free offering | Commercial / production terms | Privacy | Pakistan availability | Recommendation vs. approved architecture |
|---|---|---|---|---|---|
| **Exa** (search) | $10/month credit, resets monthly, ≈2,500 Lite searches; no card | Paid beyond credit ($4 per 1k Lite) | NOT VERIFIED | NOT VERIFIED | **Add as an option to D-SEARCH.** More free volume than Tavily (≈1,000/month) with no card. Fits ADR-012's `SearchProvider` interface; no architecture change |
| **Semantic Scholar API** (academic sources) | Public endpoints, 1,000 RPS shared by all unauthenticated users; key gives 1 RPS introductory | Commercial terms in a separate API License Agreement (NOT VERIFIED) | Public data | No restriction stated | **Add as a second research source** for scholarly claims in AI Research / Fact Checker. Read the API license before use |
| **Cloudflare Workers AI** (models) | **10,000 Neurons/day** on the Free plan; requests fail with an error when exceeded, reset 00:00 UTC | Paid plan needed above the allowance | Cloudflare docs state it **does not use customer content to train models** (VERIFIED via docs search result). A third-party report (eWEEK, 2026-10-28) describes a cross-customer data exposure incident on one model (NOT VERIFIED with Cloudflare) | NOT VERIFIED | **Candidate extra free provider** behind ADR-003 adapter; privacy terms better than Gemini free. Investigate the incident before relying on it |
| **Mistral La Plateforme "Experiment"** | Free tier exists; phone verification, no card (third-party sources); exact limits shown only in the console | Positioned for trying the API | Help centre: Experiment-plan API data **may be used for training unless you opt out** in Admin Console (search result summary; official article could not be loaded) | NOT VERIFIED | **Development only**, with training opt-out enabled. Not for tester personal data until terms are read in full |
| **Gemini API free tier** | Per-model limits (see Phase 1 free-tier report) | Unpaid terms | Content used and human-reviewed; no personal info; no EEA/UK/CH users | **Pakistan is listed as an available region (VERIFIED)** | Unchanged (D-AI) |
| **Groq free** | LIST CLAIM: 30 RPM, ~1,000–14,400 RPD by model, no card, no training | NOT VERIFIED (only paid Developer limits shown on docs) | NOT VERIFIED | NOT VERIFIED | Unchanged; owner reads limits in console |
| **NVIDIA NIM (build.nvidia.com)** | Free endpoints for Developer Program members | **"for prototyping, research, development and testing purposes only"; production needs NVIDIA AI Enterprise** (VERIFIED) | — | — | **Reject for the beta.** Acceptable only for developer experiments |
| **Cohere trial** | LIST CLAIM: 1,000 calls/month | LIST CLAIM: non-commercial only | — | — | Reject |
| **Hugging Face Inference** | LIST CLAIM: $0.10/month credit | — | — | — | Too small to matter; reject |

## 5. Shortlisted open-source projects (verified license and activity)

All last-commit dates are VERIFIED from git (2026-11-20). "Advisories" = OSV all-time / affecting latest.

### 5.1 Document parsing and OCR (M05 Knowledge Base, M08 OCR)

| Project | License (file read) | Last commit | Latest | Advisories | Hardware | Recommendation |
|---|---|---|---|---|---|---|
| **Docling** (docling-project/docling) | MIT | 2026-11-19 | 2.151.1 | 35 / 0 | Core deps are light (pydantic, docling-core, requests…); layout/table models need PyTorch (INFERRED), CPU possible but slow | **Strong candidate for Phase 9/13 ingestion** of PDF/DOCX/PPTX with tables. Complements (does not replace) pypdf. Evaluate on the 8 GB laptop before adopting; run only in the isolated worker |
| **Tesseract** | Apache-2.0 | 2026-11-19 | — | — | CPU only | **Default OCR engine for M08** (already the spec's suggestion). Needs a system install in Phase 13 |
| **OCRmyPDF** | **MPL-2.0** | 2026-11-15 | 17.14.2 | 0 / 0 | CPU; uses Tesseract + Ghostscript (INFERRED; Ghostscript is AGPL, check before bundling) | Candidate for scanned-PDF OCR. MPL-2.0 is file-level copyleft: fine as an unmodified dependency |
| **PaddleOCR** | Apache-2.0 | 2026-09-16 | 3.7.0 | 0 / 0 | CPU possible; heavier stack (PaddlePaddle) | Alternative for better multilingual/printed accuracy; Urdu support NOT VERIFIED. Evaluate only if Tesseract quality on Urdu is poor |
| **Marker / Surya** | Code Apache-2.0; **weights OpenRAIL-M, free only under $5M funding/revenue** | 2026-11-18 / 2026-11-12 | marker-pdf 2.2.0 | 0 / 0 | GPU recommended (LIST CLAIM) | **Not recommended**: weight license has a commercial threshold and usage restrictions; GPU-oriented |
| MinerU, olmOCR, EasyOCR | not reviewed in depth | — | — | — | GPU-oriented (LIST CLAIM) | Skip |

### 5.2 Speech-to-text (M09 Audio Intelligence, file-based per C5)

| Project | License | Last commit | Latest | Advisories | Hardware | Recommendation |
|---|---|---|---|---|---|---|
| **faster-whisper** (SYSTRAN) | MIT | 2026-11-12 | 1.2.1 | 0 / 0 | CPU works with small/int8 models (INFERRED); large models need much more RAM/GPU | **Candidate for M09** self-hosted transcription. On free hosts, CPU time and RAM limits make long files slow (INFERRED); pair with per-user upload caps |
| openai/whisper | MIT | 2026-08-31 | 20250625 | 0 / 0 | Needs PyTorch; slower on CPU | Reference; faster-whisper preferred |

### 5.3 Evaluation and observability (M20 Evaluation Lab, A05 Evaluation Center)

| Project | License | Last commit | Latest | Advisories | Recommendation |
|---|---|---|---|---|---|
| **promptfoo** | MIT, except `/enterprise/` directory | 2026-11-18 | npm 0.126.0 | 0 / 0 | **Candidate for prompt regression and red-teaming in CI** (prompt-injection tests required by spec 09). Node-based CLI; never use enterprise code |
| **DeepEval** | Apache-2.0 (`/enterprise/` dir present, check its terms) | 2026-11-19 | 4.3.4 | 0 / 0 | **Candidate for pytest-style evals** inside the Python backend, matching AURA's test stack. Hosted dashboard is paid (LIST CLAIM) — not needed |
| **Opik** (Comet) | Apache-2.0 | 2026-11-19 | 2.2.151 | 0 / 0 | Optional self-hosted tracing; heavier service (INFERRED). Defer |
| Arize Phoenix | **Elastic License 2.0** (not OSI; forbids offering it as a managed service) | 2026-11-19 | — | — | Usable internally only; not preferred |
| Langfuse (Phase 0) | MIT except `ee/` | — | — | — | Still an option |

### 5.4 MCP tooling (M14 Plugin/MCP Hub)

| Project | License | Last commit | Latest | Advisories | Recommendation |
|---|---|---|---|---|---|
| **FastMCP** (PrefectHQ/fastmcp) | Apache-2.0 | 2026-11-19 | 4.2.2 | 16 / 0 | **Candidate for building AURA's own MCP servers** (e.g., exposing AURA tools). The official `mcp` SDK (Phase 0) stays the client |
| MCP reference servers | MIT → Apache-2.0 transition | 2026-11-18 | — | — | Reference implementations only; each server needs a security review before use (spec M14) |
| MCP Inspector | (not reviewed) | — | — | — | Dev-only debugging tool |
| Smithery | Third-party registry | — | — | — | Not for the public beta: server quality varies (LIST CLAIM, consistent with S7) |

### 5.5 RAG frameworks and vector databases

| Project | License | Last commit | Advisories | Comparison with approved architecture | Recommendation |
|---|---|---|---|---|---|
| LlamaIndex | MIT | 2026-11-13 | llama-index-core 20 / 0 | Overlaps LangGraph + AURA's own retrieval services; adds a second abstraction layer | Not needed now |
| Haystack | Apache-2.0 | 2026-11-19 | 2 / 0 | Same overlap | Not needed now |
| RAGFlow | Apache-2.0 | 2026-11-19 | — | Separate heavy Docker stack (LIST CLAIM) | Reject on 8 GB laptop |
| **LanceDB** | Apache-2.0 (`/enterprise/` dir present) | 2026-11-19 | 0 / 0 | Embedded vector DB; would add a second datastore beside PostgreSQL | Keep **pgvector** (ADR-006); LanceDB only if pgvector fails evaluation |
| Qdrant, Chroma, Milvus, Weaviate | Phase 0 / list | — | — | Separate services | Unchanged: not needed |

### 5.6 Workflow automation (M12/M13)

| Project | License (file read) | Fit | Recommendation |
|---|---|---|---|
| Activepieces | MIT, except `packages/ee/` | A full separate automation platform (own DB, UI, workers) | **Reference only.** Embedding it would duplicate AURA's approved Workflow Engine (xyflow + procrastinate) and add a second app to host |
| Langflow | MIT | Separate platform; **84 historical advisories** (0 current) | Reject |
| Flowise | Apache-2.0 except `packages/server/src/enterprise` | Separate platform; last commit 2026-08-13 | Reject |
| Windmill | Mostly **AGPL-3.0** + proprietary enterprise | Separate platform | Reject (AGPL) |
| Dify | **Modified Apache: no multi-tenant use without written permission; logo must be kept** | AURA is multi-tenant | Reject |
| n8n | Sustainable Use License | — | Reject (Phase 0) |

### 5.7 Local model runners and open-weight models

| Project | License | Fit for AURA | Recommendation |
|---|---|---|---|
| **Ollama** | MIT (31 historical Go advisories) | Spec says avoid local LLMs on the 8 GB dev machine; production hosting of models needs GPUs (INFERRED: not free) | **Optional dev-only** adapter for a tiny model if the owner wants offline testing; not part of beta |
| LM Studio, Msty | Closed-source | — | Not components |
| Open WebUI, AnythingLLM, Jan, GPT4All, LocalAI | Various | Competing apps, not components | Reference only |
| Open-weight models (DeepSeek V4 MIT, gpt-oss Apache-2.0, Mistral Apache-2.0, Qwen/Llama/Gemma custom licenses) | LIST CLAIM | Reachable through free APIs (Groq, OpenRouter, Cloudflare) rather than self-hosting | Record per-model licenses in the Model Router catalog when a model is enabled |

### 5.8 Agents, computer-use and coding tools

| Project | Finding | Recommendation |
|---|---|---|
| OpenHands, OpenManus, AutoGPT | Heavy autonomous agents (Phase 0) | Reference only |
| browser-use, Skyvern (AGPL), UI-TARS, Agent S, ByteBot, Open Interpreter, OpenAdapt | Browser/desktop control | Out of scope until owner decides C1 otherwise |
| Aider, OpenCode, Goose | Developer tools for building AURA, not AURA components | Owner may use them personally; not integrated |
| CodeRabbit Free | LIST CLAIM: unlimited for **public** repos, summaries only on private | Limited value if the repo is private (license option L = A) |
| Qodo PR-Agent | LIST CLAIM: self-host free, you pay the LLM | Possible later; not reviewed |

## 6. Tools that could reduce AURA's costs

| Area | Tool | How it saves money | Caveat |
|---|---|---|---|
| Web search | **Exa** ($10/month resetting, no card) alongside Tavily | ≈2.5× the free search volume of Tavily | Quotas still shared; terms and privacy NOT VERIFIED |
| Academic sources | **Semantic Scholar API** | Free paper metadata and abstracts for research citations | License agreement to read |
| AI models | **Cloudflare Workers AI** (10,000 Neurons/day) | Another free provider with a no-training statement | Incident report to investigate; Neuron-to-token conversion varies by model |
| OCR | **Tesseract (+ OCRmyPDF)** self-hosted | No per-page API fees | CPU time on host |
| Document parsing | **Docling** self-hosted | Avoids paid parsing APIs (e.g., LlamaParse) | Heavier dependencies |
| Transcription | **faster-whisper** self-hosted | No per-minute STT fees | CPU/RAM on host; long files slow |
| Evaluation | **promptfoo, DeepEval** | Avoid paid evaluation SaaS | Evals that call models still use model quota |
| Object storage | Cloudflare R2 (Phase 1 verification) | No egress fees | — |

## 7. Pakistan availability

- **VERIFIED:** Pakistan is listed as an available region for the Gemini API / Google AI Studio.
- **NOT VERIFIED:** Groq, OpenRouter, Mistral, Cloudflare, Exa, Tavily, Resend, Supabase, Neon, Vercel. Most do not publish a country list on the pages checked. Practical availability (sign-up, phone verification, card acceptance for any later paid upgrade) should be confirmed by the owner when creating each account.

## 8. Comparison with the approved architecture

**No proposed addition replaces an approved technology.** Every candidate fits behind an interface already defined in the ADRs:

| Candidate | Fits behind | Effect |
|---|---|---|
| Exa, Semantic Scholar | `SearchProvider` (ADR-012) | New option for D-SEARCH |
| Cloudflare Workers AI, Mistral Experiment | `ModelProvider` via LiteLLM (ADR-003) | More free capacity; dev-only for Mistral |
| Docling, Tesseract, OCRmyPDF | `DocumentParser` in the worker (ADR-009, spec 08 file security) | Better ingestion for M05/M08 |
| faster-whisper | Audio module adapter (C5 option A) | M09 file transcription |
| promptfoo, DeepEval | Test/CI tooling and Evaluation Lab (C6 option A) | No runtime change |
| FastMCP | MCP Hub (M14) | Server-side tools only |

Rejected for conflicting with the architecture or licenses: separate workflow platforms (Activepieces, Langflow, Flowise, Windmill, Dify, n8n), extra RAG frameworks (LlamaIndex, Haystack, RAGFlow), Marker/Surya weights, Arize Phoenix (ELv2), NVIDIA NIM free (non-production), Cohere trial.

## 9. Recommendations (proposals only; nothing selected)

1. Offer **Exa** as option **D in D-SEARCH** (or Exa + Tavily together behind the interface).
2. Add **Semantic Scholar** as a secondary research source for M01/M02, subject to its API license.
3. Investigate **Cloudflare Workers AI** as an extra free model provider, including the reported incident, before D-AI is finalized.
4. Shortlist **Docling**, **Tesseract/OCRmyPDF** and **faster-whisper** for their module phases (9 and 13), with an on-laptop feasibility test then.
5. Shortlist **promptfoo** and **DeepEval** for the evaluation and prompt-injection test suites.
6. Shortlist **FastMCP** for AURA-owned MCP servers.
7. Keep all rejections above recorded in the open-source register.
