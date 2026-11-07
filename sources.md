# Official Documentation & Pricing Sources

This document catalogs all verified primary sources, official documentation pages, developer portals, and pricing sheets consulted in building and maintaining **FREE FOREVER** ([free-forever.vercel.app](https://free-forever.vercel.app)).

---

## 1. Free LLM Providers

| Provider | Official Portal / Console | Official Limits & Rate Quotas Documentation | Terms of Service & License Reference |
| :--- | :--- | :--- | :--- |
| **Google AI Studio** | [aistudio.google.com](https://aistudio.google.com/) | [Rate Limits & Quotas](https://aistudio.google.com/rate-limit) | [Gemini API Terms](https://ai.google.dev/gemini-api/terms), [Gemma Terms](https://ai.google.dev/gemma/terms) |
| **Groq Cloud** | [console.groq.com](https://console.groq.com/) | [Groq Rate Limits Documentation](https://console.groq.com/docs/rate-limits) | Model-specific licenses ([Whisper MIT](https://github.com/openai/whisper), [Qwen Apache-2.0](https://github.com/QwenLM/Qwen)) |
| **Mistral AI** | [console.mistral.ai](https://console.mistral.ai/) | [Platform Limits & Quotas](https://admin.mistral.ai/plateforme/limits) | [Mistral Terms of Service](https://mistral.ai/terms) |
| **NVIDIA NIM** | [build.nvidia.com](https://build.nvidia.com/) | [NVIDIA API Catalog & Trial Limits](https://build.nvidia.com) | [NVIDIA API Trial Terms](https://build.nvidia.com) |
| **OpenRouter** | [openrouter.ai](https://openrouter.ai/) | [Free Model Limits & Quotas](https://openrouter.ai/docs/api_reference/limits) | [OpenRouter Terms of Service](https://openrouter.ai/terms) |
| **Cerebras Cloud** | [cloud.cerebras.ai](https://cloud.cerebras.ai/) | [Cerebras Inference Rate Limits](https://inference-docs.cerebras.ai/support/rate-limits) | [OpenAI Open Weights License](https://openai.com) |

---

## 2. Free Cloud Hosting & Deployment Platforms

| Platform | Category | Official Pricing / Free Tier Source | Documentation / Limits Reference |
| :--- | :--- | :--- | :--- |
| **Vercel** | Static Sites, Serverless & Edge | [Vercel Hobby Plan Pricing](https://vercel.com/pricing) | [Hobby Limits](https://vercel.com/docs/plans/hobby), [Function Limitations](https://vercel.com/docs/functions/limitations), [Edge Functions](https://vercel.com/docs/functions/runtimes/edge), [Blob Limits](https://vercel.com/docs/vercel-blob/usage-and-pricing) |
| **Netlify** | Static Sites, Functions & DB | [Netlify Pricing](https://www.netlify.com/pricing/) | [Credit-Based Plans](https://docs.netlify.com/manage/accounts-and-billing/billing/billing-for-credit-based-plans/credit-based-pricing-plans), [Function Configuration](https://docs.netlify.com/build/functions/configuration), [Edge Functions](https://docs.netlify.com/build/edge-functions/limits), [Background Functions](https://docs.netlify.com/build/functions/background-functions), [Netlify DB](https://docs.netlify.com/build/data-and-storage/netlify-database/billing-and-usage) |
| **Railway** | Web Services & Containers | [Railway Pricing](https://railway.com/pricing) | [Free Trial Limits](https://docs.railway.com/pricing/free-trial) |
| **Render** | Web Services & Static Sites | [Render Pricing](https://render.com/pricing) | [Free Tier Guide](https://render.com/docs/free), [Static Sites](https://render.com/docs/static-sites) |
| **Supabase** | BaaS, Postgres & Edge Functions | [Supabase Pricing](https://supabase.com/pricing) | [Edge Functions Limits](https://supabase.com/docs/guides/functions/limits) |
| **Cloudflare Pages** | Jamstack & Edge Hosting | [Cloudflare Pages Pricing](https://pages.cloudflare.com/) | [Pages Platform Limits](https://developers.cloudflare.com/pages/platform/limits/), [Workers Limits](https://developers.cloudflare.com/workers/platform/limits/) |
| **GitHub Pages** | Static Site Hosting | [GitHub Pages Overview](https://pages.github.com/) | [GitHub Pages Limits](https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits) |
| **Google Cloud Run** | Serverless Containers | [Google Cloud Run Pricing](https://cloud.google.com/run/pricing) | [Free Tier Quotas (2M requests/mo)](https://cloud.google.com/run/pricing) |
| **Oracle Cloud** | Always Free Compute & DB | [Oracle Always Free Tier](https://www.oracle.com/cloud/free/) | [Always Free Resources Documentation](https://docs.oracle.com/iaas/Content/FreeTier/freetier_topic-Always_Free_Resources.htm) |
| **Fly.io** | MicroVMs & Containers | [Fly.io Pricing](https://fly.io/pricing/) | [Pricing & Allowance Docs](https://docs.fly.io/about/pricing) |
| **Deno Deploy** | Edge Functions | [Deno Deploy Pricing](https://deno.com/deploy/pricing) | [Deploy Documentation](https://docs.deno.com/deploy) |
| **Trigger.dev** | Background Jobs & Workflows | [Trigger.dev Pricing](https://trigger.dev/pricing) | [Documentation & Quotas](https://trigger.dev/docs) |

---

## 3. Automated Verification & Auditing Policy

All sources listed above are audited automatically by our **GitHub Actions Limits Monitor**:
1. Every URL is retrieved and parsed into normalized text content.
2. Cryptographic SHA-256 hashes are computed to identify any documentation updates instantly.
3. Upon detecting content drift, our workflow leverages LLM parsing (`nvidia/nemotron-3-ultra-550b-a55b`) to extract updated values and append audit alerts to [`data/alerts.csv`](./data/alerts.csv) for human verification.
4. Verified updates are merged into production CSVs in [`data/`](./data/).

---

## 4. Community Corrections & Additions

If you find that an upstream URL has changed, moved, or if a provider has updated their pricing structure, please feel free to open a Pull Request or issue on our GitHub repository. We actively welcome contributions to keep all listings 100% up to date.
