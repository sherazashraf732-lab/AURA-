# PHASE 1 — Free Tier Verification

- **Date checked:** 2026-11-20 (official pages fetched live)
- **Rule applied:** Nothing is called "free" unless the provider's own page says so. Where a page did not state a fact, it is marked **NOT STATED** or **NOT VERIFIED**. No account was created and no key was used.
- **Key point for AURA:** every quota below belongs to **one AURA account and is shared by all 50–100 testers**, not given per tester.

## 1. AI model providers

| Provider | What is actually free (VERIFIED from official page) | Restrictions that matter for AURA | Source |
|---|---|---|---|
| **Google Gemini API (AI Studio)** | A free tier exists, per model. Example listed: 200 RPM, 50,000 TPM, 10,000 RPD for one model; some newer models are **not available** on the free tier. Needs an active project; some projects need verification. | **Terms for unpaid services:** Google "uses the content you submit … to provide, improve, and develop" its products; "human reviewers may read, annotate, and process your API input and output"; "Do not submit sensitive, confidential, or personal information to the Unpaid Services." Unpaid services **may not be used to serve users in the EEA, UK or Switzerland**. | aistudio.google.com/docs/rate-limits, aistudio.google.com/docs/terms |
| **Groq** | Free tier exists ("Free tier rate limits" referenced). **Free-tier numbers were NOT shown** on the docs page; only Developer (paid) base limits were shown (e.g., 30 RPM / 1K RPD / 8K TPM / 200K TPD for gpt-oss-120b). Spend limits are **not available** on free accounts. | Free limits NOT VERIFIED; must be read in the console after sign-up. Data-use terms NOT VERIFIED. | console.groq.com/docs/rate-limits, /docs/spend-limits, /docs/billing-faqs |
| **OpenRouter** | `:free` models: **20 requests/minute and 50 requests/day** if under 10 credits were ever purchased; 1,000/day after buying at least 10 credits (buying credits is paid). | 50 requests/day for the whole platform is far too low for 50–100 testers. Raising it requires a purchase (owner approval). Per-model data policies vary (NOT VERIFIED). | openrouter.ai/docs/api-reference/limits |
| **Cerebras** | **Free Trial only:** $5 of credits that **expire after 30 days**; e.g., 5 RPM / 1M TPD for gpt-oss-120b. | **Not a permanent free tier.** Treat as trial only. | inference-docs.cerebras.ai/support/rate-limits |
| Anthropic, OpenAI | Paid APIs (keys present as placeholders in `.env.example`) | Off by default; explicit approval only | — |

**Conclusion (INFERRED from the above):** No provider offers a free tier that is both privacy-safe for public users' personal data and large enough for 100 testers. Gemini's free tier is the largest but its terms forbid sending personal information and allow human review, which conflicts with AURA's privacy rules unless testers are clearly told and agree. Options for the owner (decision D-AI, presented in the Phase 1 report):

1. Free tiers for development and a small closed beta, with a clear tester notice and consent, a strict per-user daily cap, and no EEA/UK/Swiss users on Gemini's free tier.
2. Bring-your-own-key: testers paste their own free-tier keys (their quota, their consent).
3. A small paid budget with a hard spend cap (requires owner approval; default stays $0).

## 2. Web search for AI Research

| Service | Free offering (VERIFIED) | Restrictions |
|---|---|---|
| **Tavily** | Researcher plan: **1,000 API credits/month, no credit card required**. Advanced requests use more credits. Pay-as-you-go is $0.008/credit. | ~1,000 basic searches/month shared by all users |
| **Brave Search API** | **$5 free credits/month** (≈1,000 requests at $5/1,000, INFERRED); 50 queries/second. **Credit card required.** Page banner also says "up to $20" (inconsistent). | **Storing results is not allowed** on standard plans; card on file |
| **SearXNG (self-hosted)** | Software is free (AGPL-3.0) | Needs a server; relies on upstream engines that may block; AGPL applies to SearXNG itself |

## 3. Database, auth and storage

| Service | Free offering (VERIFIED) | Restrictions |
|---|---|---|
| **Supabase Free** | 500 MB database (shared CPU, 500 MB RAM), 1 GB file storage, 5 GB egress + 5 GB cached egress, 50,000 auth MAUs, 2 active projects | **Paused after 1 week of inactivity.** Auth email rate limits and pgvector NOT STATED on pricing page (pgvector is commonly available, NOT VERIFIED here). |
| **Neon Free** | 1 GB Postgres storage per project (20 GB total), 100 CU-hours/project/month, 100 projects, pgvector included, 5 GB object storage per project | Compute scales to zero after 5 minutes idle (cold start); compute suspends when CU-hours run out until next month |
| **Cloudflare R2** (object storage) | 10 GB-month storage, 1M Class A ops, 10M Class B ops per month; **no egress fees** | Free tier only for Standard storage; payment method requirement NOT STATED on the page |

## 4. Hosting

| Service | Free offering (VERIFIED) | Restrictions |
|---|---|---|
| **Vercel Hobby** | 100 GB data transfer, 1M function invocations, 4 CPU-hours, 360 GB-hrs memory, 200 projects, 100 deployments/day | **Terms §4: "You shall only use the Services under a Hobby plan for your personal or non-commercial use."** Usage over limits pauses the feature for up to 30 days; no paid overage on Hobby. A free, non-commercial beta fits; any commercial use needs Pro ($20/user/month) or another host. |
| **Render Free** | **NOT VERIFIED.** render.com/docs/free and /pricing both failed to load (connection reset, three attempts). | Must be verified before choosing Render for the API/worker |
| Other API hosts | Not researched yet | Candidates to verify in Phase 2 if Render remains unverifiable |

## 5. Email (verification and password reset)

| Service | Free offering (VERIFIED) | Restrictions |
|---|---|---|
| **Resend Free** | **100 emails/day, 3,000/month**, 3 domains | Card requirement NOT STATED; needs a domain you control for production sending |

## 6. Error monitoring

| Service | Free offering (VERIFIED) | Restrictions |
|---|---|---|
| **Sentry Developer** | 5k errors (period NOT STATED on page), 1 user, 30-day lookback | Must scrub personal data before sending events |

## 7. What this means for AURA's defaults

- `ALLOW_PAID_PROVIDER_USAGE=false` and `GLOBAL_DAILY_SPEND_LIMIT=0` stay as they are.
- The Model Router must treat **provider quota as shared and global**, enforce per-user caps beneath it, and show "quota reached" instead of switching to a paid provider.
- A tester consent screen must disclose which provider receives their messages and that free-tier providers may use and review the data.
- Hosting choices need re-verification right before deployment (Phase 14/15), because these terms change often.
