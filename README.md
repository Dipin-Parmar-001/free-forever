<div align="center">

# ⚡ FREE FOREVER

**Every free LLM. Every free hosting tier. Real limits, tested latency, and zero BS.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Daily Limits Monitor](https://github.com/Dipin-Parmar-001/free-forever/actions/workflows/limits-monitor.yml/badge.svg)](https://github.com/Dipin-Parmar-001/free-forever/actions/workflows/limits-monitor.yml)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](https://github.com/Dipin-Parmar-001/free-forever/pulls)

[**Live Demo**](https://dipin-parmar-001.github.io/free-forever/) • [**Data Sources**](./sources.md) • [**Methodology**](./data_collection.md)

</div>

---

## 📌 Overview

**FREE FOREVER** is a developer-first directory and live intelligence dashboard curating truly free computing resources:
1. **Free LLM API Directory**: Track context windows, daily rate limits (RPD/RPM/TPM), tool calling, reasoning support, and empirically measured latency (TTFT, p50, p95).
2. **Free Hosting & Deployment Registry**: Discover free-tier hosting across Serverless, Edge, Web Services, Docker, and Managed Databases.
3. **The Essential Filter Nobody Else Gives You**: Instantly filter out platforms that demand a **Credit Card** or **Phone Number** up-front.

All data is kept evergreen using a **SHA-256 automated hash diff monitor** running daily via GitHub Actions with AI-assisted schema extraction and human sign-off.

---

## ✨ Features

- 🚫 **"No Card, No Phone" Toggles**: Stop wasting hours signing up only to hit a credit card wall.
- ⏱️ **First-Party Empirical Benchmarking**: Real response times, TTFT, and reliability measured directly from our test harness in India.
- 🔍 **Multi-dimensional Search & Filtering**:
  - Filter by Provider (Google AI Studio, Groq, Mistral, Cerebras, NVIDIA NIM, OpenRouter).
  - Filter by Capabilities (Reasoning, Tool Calling, Vision/Multimodal, Audio transcription, TTS).
  - Sort by Daily Budget (RPD), Request Throughput (RPM), Context Window, or Lowest Latency.
- ⚡ **Zero-Dependency Interactive UI**: A single ultra-responsive, beautiful frontend (`free-forever.html`) with brutalist design aesthetics, dark/light theme support, and instantaneous client-side filtering.
- 🤖 **Automated Daily Drift Detection**: GitHub Actions monitors upstream documentation daily and logs diffs when providers modify their quotas.

---

## 🏗️ Architecture & Project Structure

```text
FREE FOREVER/
├── .github/
│   └── workflows/
│       └── limits-monitor.yml      # Daily automated limits crawler & diff detector
├── app/
│   ├── free-forever.html           # Full interactive client-side web application
│   └── limits_monitor_workflow.py  # Automation script checking URL hashes & schema diffs
├── data/                           # Production datasets (committed to repository)
│   ├── deployment_platforms_offerings_final.xlsx
│   ├── free_llm_directory_schema-offering.csv
│   └── free_llm_directory_schema-messurments.csv
├── .gitignore                      # Configured to protect secrets, raw tests & working data
├── data_collection.md              # Detailed collection & empirical benchmarking methodology
├── requirements.txt                # Python dependencies for monitoring workflow
├── sources.md                      # Index of all official documentation & pricing URLs
└── README.md                       # Main project documentation
```

---

## 🚀 Getting Started

### Running the Web Application Locally

The frontend has zero build steps and no heavy node_modules:
1. Clone the repository:
   ```bash
   git clone https://github.com/Dipin-Parmar-001/free-forever.git
   cd free-forever
   ```
2. Open `app/free-forever.html` directly in any modern web browser or serve via Python:
   ```bash
   python -m http.server 8000 --directory app
   ```
3. Visit `http://localhost:8000/free-forever.html`.

---

### Running the Limits Monitor Locally

To run the automated hash-diff and LLM-assisted quota extractor locally:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Set your environment variable** (for AI parsing when documentation changes):
   ```bash
   # Create a .env file:
   NVIDIA_API_KEY=your_nvidia_nim_api_key_here
   ```
3. **Execute the workflow**:
   ```bash
   python app/limits_monitor_workflow.py
   ```

---

## 🔄 Automated CI/CD (GitHub Actions)

A scheduled GitHub Action (`.github/workflows/limits-monitor.yml`) runs every 24 hours at `00:00 UTC`:
- Fetches all URLs tracked in the directory.
- Calculates SHA-256 hashes of stripped HTML text.
- If upstream documentation changes, parses new limits using `nvidia/nemotron-3-ultra-550b-a55b`.
- Logs detected quota updates into `alerts.csv` and updates timestamps automatically.

---

## 📊 Data Verification & Sources

- For a complete list of verified provider pages, consult [**`sources.md`**](./sources.md).
- To read how measurements and empirical benchmarks were gathered, consult [**`data_collection.md`**](./data_collection.md).

---

## 👨‍💻 Author

**Dipin Parmar**
- **LinkedIn**: [linkedin.com/in/dipin-parmar-1119b5385](https://www.linkedin.com/in/dipin-parmar-1119b5385)
- **GitHub**: [@Dipin-Parmar-001](https://github.com/Dipin-Parmar-001)

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

