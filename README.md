<div align="center">

# ⚡ FREE FOREVER

**Every free LLM. Every free hosting tier. Real limits, tested latency, and zero BS.**

[![Live Web App](https://img.shields.io/badge/Live%20App-free--forever.netlify.app-00ad9f?style=for-the-badge&logo=netlify&logoColor=white)](https://free-forever.netlify.app/)
[![Daily Limits Monitor](https://img.shields.io/github/actions/workflow/status/Dipin-Parmar-001/free-forever/limits-monitor.yml?branch=main&label=Daily%20Limits%20Monitor&style=for-the-badge)](https://github.com/Dipin-Parmar-001/free-forever/actions/workflows/limits-monitor.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=for-the-badge)](https://github.com/Dipin-Parmar-001/free-forever/pulls)

### 🌐 [https://free-forever.netlify.app/](https://free-forever.netlify.app/)

[**Live Application**](https://free-forever.netlify.app/) • [**Verified Sources**](./sources.md) • [**Data Collection & Benchmarks**](./data_collection.md) • [**Contributing**](#-contributing--community-updates)

</div>

---

## 📌 Overview

**FREE FOREVER** is a developer-first directory and live intelligence dashboard curating truly free computing and AI resources:
1. **Free LLM API Directory**: Track context windows, daily rate limits (RPD/RPM/TPM), tool calling, streaming, reasoning support, and empirically measured latencies (TTFT, p50, p95).
2. **Free Hosting & Deployment Registry**: Discover free-tier hosting across Serverless, Edge, Web Services, Docker containers, Background Workers, and Managed Databases.
3. **The Essential Filter Nobody Else Gives You**: Instantly filter out platforms that demand a **Credit Card** or **Phone Number** up-front.

All data is kept evergreen using a **SHA-256 automated hash diff monitor** running daily via GitHub Actions with AI-assisted schema extraction and human sign-off.

---

## ✨ Features

- 🚫 **"No Card, No Phone" Toggles**: Stop wasting hours signing up only to hit a credit card or phone wall.
- ⏱️ **First-Party Empirical Benchmarking**: Real response times, TTFT, and reliability measured directly from our test harness in India.
- 🔍 **Multi-dimensional Search & Filtering**:
  - Filter by Provider (Google AI Studio, Groq, Mistral, Cerebras, NVIDIA NIM, OpenRouter).
  - Filter by Capabilities (Reasoning, Tool Calling, Vision/Multimodal, Audio transcription, TTS).
  - Sort by Daily Budget (RPD), Request Throughput (RPM), Context Window, or Lowest Latency.
- ⚡ **Zero-Dependency Interactive UI**: A single ultra-responsive, beautiful frontend (`app/index.html`) deployed globally on Netlify with brutalist design aesthetics, dark/light theme support, and instantaneous client-side filtering.
- 🤖 **Automated Daily Drift Detection**: GitHub Actions monitors upstream documentation daily and logs diffs into `data/alerts.csv` whenever providers adjust quotas.

---

## 🏗️ Repository & Final Project Structure

```text
FREE FOREVER/
├── .github/
│   └── workflows/
│       └── limits-monitor.yml                    # Daily automated limits crawler & diff detector
├── app/
│   ├── index.html                                # Production single-page web application
│   └── limits_monitor_workflow.py                # Automated workflow monitoring live URL hashes & CSV diffs
├── data/                                         # Production datasets & audit trail
│   ├── alerts.csv                                # Log of detected drift & rate limit updates
│   ├── deployment_platforms_offerings_final.csv  # 26 verified cloud hosting free offerings
│   ├── deployment_platforms_platforms_final.csv  # 12 verified deployment platforms
│   ├── deployment_platforms_offerings_final.xlsx # Source workbook
│   ├── free_llm_directory_schema-offering.csv    # 50+ free LLM offerings & rate limits
│   ├── free_llm_directory_schema-messurments.csv # First-party latency & reliability measurements
│   └── url_content_hashes.json                   # Cryptographic SHA-256 hashes of monitored docs
├── .gitignore                                    # Production gitignore (keeps raw benchmarks local)
├── data_collection.md                            # Comprehensive collection & benchmarking methodology
├── LICENSE                                       # MIT License
├── requirements.txt                              # Python dependencies for the monitoring engine
├── sources.md                                    # Comprehensive index of verified documentation URLs
└── README.md                                     # Main project documentation
```

---

## 🚀 Running Locally

### 1. Web Application
The frontend requires zero build tools or package managers:
```bash
# Clone the repository
git clone https://github.com/Dipin-Parmar-001/free-forever.git
cd free-forever

# Serve using Python's built-in HTTP server
python -m http.server 8000 --directory app
```
Navigate to `http://localhost:8000/index.html` (or `http://localhost:8000`) in your browser.

---

### 2. Limits & Quotas Monitoring Workflow
The monitoring script can be run locally to inspect upstream documentation for changes:

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure NVIDIA API Key (used for structured schema extraction on diffs)
# Create a .env file with:
NVIDIA_API_KEY=your_nvidia_nim_api_key_here

# 3. Run the workflow
python app/limits_monitor_workflow.py
```

The script will:
- Read production CSV files in [`data/`](./data/).
- Compute SHA-256 hashes of live documentation pages.
- Flag any changed limits and log updates into [`data/alerts.csv`](./data/alerts.csv).

---

## 🔄 Automated CI/CD (GitHub Actions)

A scheduled GitHub Action ([`.github/workflows/limits-monitor.yml`](./.github/workflows/limits-monitor.yml)) executes every day at **00:00 UTC**:
1. Checks out the repository and sets up Python 3.11.
2. Runs [`app/limits_monitor_workflow.py`](./app/limits_monitor_workflow.py).
3. If upstream documentation drifts, extracts updated limits using `nvidia/nemotron-3-ultra-550b-a55b`.
4. Appends audit records to `data/alerts.csv` and auto-commits timestamp updates.

---

## 🤝 Contributing & Community Updates

We actively welcome and encourage contributions from the developer community! Free tiers evolve rapidly, and your help in keeping this registry accurate, honest, and comprehensive is invaluable.

### Ways you can contribute:
- **Add New Free Offerings**: Found a generous free LLM API or hosting tier with real free allowances? Submit a PR!
- **Correct Outdated Limits**: Notice a provider lowered their RPM, changed their context window, or added a card requirement? Help us correct it.
- **Report Broken Links or Changes**: Open an issue if a documentation URL moved or a platform changed their pricing model.
- **Submit Latency Benchmarks**: Share benchmark measurements from different regions.

### How to submit a change:
1. Fork the repository.
2. Edit the corresponding CSV file in `data/`:
   - For LLMs: `data/free_llm_directory_schema-offering.csv`
   - For Hosting: `data/deployment_platforms_offerings_final.csv`
3. Provide the official documentation or pricing link in `LIMITS_SOURCE_URL` / `source_url`.
4. Open a Pull Request detailing the changes and sources.

---

## 📊 Data Verification & Sources

- **Complete List of Verified URLs**: Consult [**`sources.md`**](./sources.md).
- **Data Collection & Benchmarking Architecture**: Consult [**`data_collection.md`**](./data_collection.md).

---

## 👨‍💻 Author

**Dipin Parmar**
- **Live Deployment**: [free-forever.netlify.app](https://free-forever.netlify.app/)
- **LinkedIn**: [linkedin.com/in/dipin-parmar-1119b5385](https://www.linkedin.com/in/dipin-parmar-1119b5385)
- **GitHub**: [@Dipin-Parmar-001](https://github.com/Dipin-Parmar-001)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).
