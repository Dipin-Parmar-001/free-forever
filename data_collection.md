# Data Collection & Verification Methodology

**FREE FOREVER** ([free-forever.netlify.app](https://free-forever.netlify.app/)) is committed to providing 100% transparent, verified, and actionable intelligence on free LLM APIs and free cloud deployment tiers. This document details the hybrid architecture used to discover, curate, benchmark, and maintain the dataset.

---

## 1. The Core Problem with "Free" Tiers

Most online developer directories and aggregator sites are quickly outdated or obscure critical signup hurdles:
- **Hidden friction**: Many "free" tiers require a valid credit card or strict SMS phone verification.
- **Unstated limits**: Quotas are often buried across disparate documentation pages, terms of service, or hidden behind API response headers.
- **Silent tier deprecations**: Platforms adjust memory limits, sleep timeouts, or request budgets without notice.

To solve this, our system employs a **three-tier data verification methodology**:
1. **AI-Assisted Automated Extraction & Ingestion**
2. **First-Party Empirical Benchmark Testing**
3. **Rigorous Human Verification, Community Contributions & Hash-Diff Auditing**

```
┌────────────────────────────────┐
│ Official Docs & Pricing Pages │
└──────────────┬─────────────────┘
               │ (Crawled & Hashed)
               ▼
┌────────────────────────────────┐
│   Automated Hash-Diff Engine   │
└──────────────┬─────────────────┘
               │ (When hash changes)
               ▼
┌────────────────────────────────┐
│ AI Extraction & Structured NLP │ (NVIDIA Nemotron 3 Ultra)
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ Empirical Benchmarking Engine  │ (Live API calls: latency, TTFT, TPS, error rates)
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│   Human Review & Approval      │ (Final sign-off before production release)
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│ Community Feedback & PRs       │ (Crowdsourced corrections & new additions)
└────────────────────────────────┘
```

---

## 2. Methodology Breakdown

### Phase 1: AI-Assisted Data Extraction

1. **Target Identification**: We systematically tracked 12+ cloud platforms and 6 major AI inference providers.
2. **Text Normalization**: Web pages and pricing docs are ingested, stripped of transient scripts/styles/SVGs, and converted into deterministic text streams.
3. **Structured Schema Parsing**: Where numbers or limits are ambiguous in raw markdown/HTML, frontier language models (`nvidia/nemotron-3-ultra-550b-a55b`) extract structured attributes adhering strictly to our schema (e.g., `requests_quota`, `ram_mb`, `idle_timeout_min`, `overage_behavior`).

### Phase 2: Live Empirical Benchmarking (Own-Tested Numbers)

Whenever an API provider did not publish authoritative latency or throughput metrics, we did not rely on marketing claims. Instead, we wrote dedicated Python benchmarking suites and measured performance directly:
- **Locations Tested**: Originating from India (`reg: India`).
- **Metrics Collected**:
  - **TTFT (Time To First Token)**: Exact milliseconds until streaming begins.
  - **Latency (Full Response Time)**: End-to-end duration for standardized prompts.
  - **Percentiles**: Median (p50) and 95th percentile (p95) latency over 20–30 repeated executions.
  - **Throughput (Tokens Per Second)**: Measured output tokens divided by streaming duration.
  - **Error Rates & HTTP Statuses**: Explicit logging of `HTTP 429` (rate limits) and `HTTP 503` (service capacity limits).

*Examples from our benchmarking harness:*
- `google_ai_studio__gemini-3-8-flash`: Verified 5 RPM, 250K TPM, 20 RPD.
- `groq__openai-gpt-oss-20b`: Measured ~1.19s latency, p95 1.36s, 100% success rate across 30 test runs.
- `mistral_studio__codestral-2508`: Measured 1.83s latency with full tool-calling and FIM support.

### Phase 3: Human Verification & Sign-off

- No AI-extracted change is promoted directly to public-facing production files without human inspection.
- When differences are flagged, they are recorded into [`data/alerts.csv`](./data/alerts.csv) for review.
- Every row contains a `last_verified` date and a `verified_by` audit trail (e.g., `docs`, `own_tested`, `pricing_page`).

---

## 3. Continuous Monitoring via GitHub Actions

To ensure the registry remains evergreen, a daily scheduled workflow (`.github/workflows/limits-monitor.yml`) executes at 00:00 UTC:
1. Calculates SHA-256 hashes for all monitored endpoints.
2. Compares hashes against [`data/url_content_hashes.json`](./data/url_content_hashes.json).
3. If an endpoint's hash changes, only that specific URL is re-parsed to discover newly adjusted numbers.
4. Alerts are logged with old vs. new values and committed automatically for maintainer review.

---

## 4. Community Contributions & Corrections

The ecosystem of developer tools and LLM platforms moves at a rapid pace. We actively encourage developers and platform maintainers to help keep the data accurate:
- **Found a new free tier?** We welcome submissions for any service offering permanent free usage, recurring credits, or generous developer trials.
- **Noticed a changed limit?** If a provider adjusted their RPM, changed idle timeouts, or started requesting credit cards, submit an edit to the CSV files in `data/`.
- **Contribute PRs**: All datasets live as plain CSVs in `data/` for easy reviewing and git diff inspection.
