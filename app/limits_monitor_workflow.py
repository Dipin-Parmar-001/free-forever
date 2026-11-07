import os
import re
import csv
import json
import hashlib
from datetime import datetime
from pathlib import Path
from html.parser import HTMLParser
import requests
from dotenv import load_dotenv

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent

# Input directory (Defaults to 'data' for repo production/GitHub Actions; can fallback to 'copy_data')
DATA_DIR = PROJECT_ROOT / "data"
COPY_DATA_DIR = PROJECT_ROOT / "copy_data"
TARGET_DIR = DATA_DIR if DATA_DIR.exists() else COPY_DATA_DIR

# LLM Offerings Dataset
LLM_CSV_PATH = TARGET_DIR / "free_llm_directory_schema-offering.csv"

# Deployment Platforms Dataset (Checks new CSV file; fallback to copy_data naming if needed)
DEPLOYMENT_CSV_PATH = TARGET_DIR / "deployment_platforms_offerings_final.csv"
if not DEPLOYMENT_CSV_PATH.exists():
    DEPLOYMENT_CSV_PATH = TARGET_DIR / "deployment_platforms_offerings_final-offerings.csv"

# Hash cache and alerts file
HASHES_JSON_PATH = TARGET_DIR / "url_content_hashes.json"
ALERTS_CSV_PATH = TARGET_DIR / "alerts.csv"

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
NVIDIA_API_URL = "https://integrate.api.nvidia.com/v1/chat/completions"
MODEL_NAME = "nvidia/nemotron-3-ultra-550b-a55b"

# Deployment fields to monitor
DEPLOYMENT_MONITORED_FIELDS = [
    # Compute
    "ram_mb",
    "vcpu",
    "gpu_available",
    # Runtime
    "execution_model",
    "idle_timeout_min",
    "max_request_timeout_s",
    # Quotas & Limits
    "bandwidth_gb_month",
    "build_quota",
    "build_quota_unit",
    "build_quota_period",
    "requests_quota",
    "requests_period",
    "persistent_storage_gb",
    "max_projects_or_services",
    # Free Type & Credits
    "free_type",
    "credit_amount",
    "credit_unit",
    "credit_period",
    "trial_or_credit_days",
]


class HTMLTextExtractor(HTMLParser):
    """Clean text extractor from HTML pages stripping scripts, styles, and other metadata."""
    def __init__(self):
        super().__init__()
        self.texts = []
        self.ignore = False

    def handle_starttag(self, tag, attrs):
        if tag.lower() in ["script", "style", "svg", "noscript", "iframe"]:
            self.ignore = True

    def handle_endtag(self, tag):
        if tag.lower() in ["script", "style", "svg", "noscript", "iframe"]:
            self.ignore = False

    def handle_data(self, data):
        if not self.ignore:
            cleaned = data.strip()
            if cleaned:
                self.texts.append(cleaned)

    def get_text(self):
        return re.sub(r"\s+", " ", " ".join(self.texts)).strip()


def compute_content_hash(text: str) -> str:
    """Computes SHA-256 hash of normalized text."""
    normalized = re.sub(r"\s+", " ", text).strip()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def load_hashes() -> dict:
    if HASHES_JSON_PATH.exists():
        try:
            with open(HASHES_JSON_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Failed to load {HASHES_JSON_PATH}: {e}")
    return {}


def save_hashes(hashes: dict):
    with open(HASHES_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(hashes, f, indent=2, ensure_ascii=False)


def append_alert(offering_id: str, provider_id: str, item_name: str, source_url: str, field_name: str, old_value: str, new_value: str, dataset_type: str = "llm"):
    """Appends an alert row when limits or quotas change."""
    file_exists = ALERTS_CSV_PATH.exists()
    timestamp = datetime.now().astimezone().isoformat()
    
    with open(ALERTS_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "TIMESTAMP",
                "DATASET_TYPE",
                "OFFERING_ID",
                "PROVIDER_ID",
                "ITEM_NAME",
                "SOURCE_URL",
                "FIELD_NAME",
                "OLD_VALUE",
                "NEW_VALUE"
            ])
        writer.writerow([
            timestamp,
            dataset_type,
            offering_id,
            provider_id,
            item_name,
            source_url,
            field_name,
            old_value,
            new_value
        ])


def parse_numeric_limit(val):
    if val is None:
        return None
    val_str = str(val).strip().lower()
    if not val_str or val_str in ["null", "none", "unknown", "n/a", "-", ""]:
        return None
    
    # Handle shorthand like 14.4k, 8k, 250k
    m = re.match(r"^([\d\.]+)\s*k$", val_str)
    if m:
        try:
            return int(float(m.group(1)) * 1000)
        except ValueError:
            pass
            
    m = re.match(r"^([\d\.]+)\s*m$", val_str)
    if m:
        try:
            return int(float(m.group(1)) * 1000000)
        except ValueError:
            pass
            
    m = re.match(r"^([\d\.]+)\s*g[b]?$", val_str)
    if m:
        try:
            return int(float(m.group(1)))
        except ValueError:
            pass

    clean_digits = re.sub(r"[^\d\.]", "", val_str)
    if clean_digits:
        try:
            return int(float(clean_digits))
        except ValueError:
            pass
    return None


def normalize_val(val):
    """Normalize string, boolean, and synonym values for robust comparison."""
    if val is None:
        return ""
    v = str(val).strip()
    v_lower = v.lower()
    if v_lower in ["null", "none", "n/a", "unknown", "-", ""]:
        return ""
    if v_lower in ["true", "t", "yes", "1"]:
        return "true"
    if v_lower in ["false", "f", "no", "0"]:
        return "false"
    # Canonicalize common equivalent synonyms
    if v_lower in ["once", "one_time", "one-time", "single"]:
        return "one_time"
    if v_lower in ["permanent", "always", "recurring", "recurring_credit"]:
        return "permanent"
    if v_lower in ["usd", "$"]:
        return "usd"
    return v_lower


def values_differ(curr_val, new_val) -> bool:
    """Returns True if there is a substantive difference between current and extracted values."""
    curr_norm = normalize_val(curr_val)
    new_norm = normalize_val(new_val)

    if not curr_norm or not new_norm:
        return False

    # Check numeric comparison first
    curr_num = parse_numeric_limit(curr_val)
    new_num = parse_numeric_limit(new_val)
    if curr_num is not None and new_num is not None:
        return curr_num != new_num

    return curr_norm != new_norm


def fetch_url_content(url: str) -> str:
    """Fetches URL content and extracts visible clean text."""
    cleaned_url = url.strip()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }
    response = requests.get(cleaned_url, headers=headers, timeout=25)
    response.raise_for_status()
    
    parser = HTMLTextExtractor()
    parser.feed(response.text)
    return parser.get_text()


def call_nemotron(system_prompt: str, user_prompt: str) -> str:
    if not NVIDIA_API_KEY:
        raise ValueError("NVIDIA_API_KEY is not set in environment or .env file.")

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        "max_tokens": 4096,
        "temperature": 0.1
    }

    resp = requests.post(
        NVIDIA_API_URL,
        headers={"Authorization": f"Bearer {NVIDIA_API_KEY}", "Content-Type": "application/json"},
        json=payload,
        timeout=150
    )
    resp.raise_for_status()
    result_data = resp.json()
    choice_msg = result_data["choices"][0]["message"]
    raw_content = choice_msg.get("content") or ""
    
    match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_content)
    if match:
        raw_content = match.group(1).strip()
    return raw_content


def extract_llm_limits_with_nemotron(page_text: str, target_models: list) -> list:
    """Calls NVIDIA NIM nemotron-3-ultra-550b-a55b to extract LLM rate limits."""
    model_list_str = ", ".join([f"'{m}'" for m in target_models])
    content_slice = page_text[:12000]

    system_prompt = (
        "You are an expert rate limit extractor. Extract rate limits for specified models from the provided documentation text.\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Extract ONLY from the FREE / FREE TRIAL / HOBBY tier tables. Do NOT extract from Developer, Pay-as-you-go, or Enterprise tiers.\n"
        "2. If a model appears under both Free and Paid sections, extract strictly the Free tier values.\n"
        "Return STRICTLY a valid JSON object with a single key 'models' containing an array of objects:\n"
        "{\n"
        '  "models": [\n'
        '    {"model_name": "exact or matching model name", "rpm": number or null, "rpd": number or null, "tpm": number or null, "tpd": number or null}\n'
        "  ]\n"
        "}\n"
        "Do not include commentary or markdown fences. Return ONLY the JSON object."
    )

    user_prompt = (
        f"Documentation page content:\n{content_slice}\n\n"
        f"Extract Free / Free Trial tier rate limits (RPM, RPD, TPM, TPD) for these models if present: {model_list_str}."
    )

    raw_content = call_nemotron(system_prompt, user_prompt)
    try:
        parsed = json.loads(raw_content)
        if isinstance(parsed, dict) and "models" in parsed:
            return parsed["models"]
        elif isinstance(parsed, list):
            return parsed
    except Exception as e:
        print(f"[WARN] Failed to parse LLM Nemotron JSON response: {e}\nRaw output: {raw_content[:300]}")
    return []


def extract_deployment_limits_with_nemotron(page_text: str, target_products: list) -> list:
    """Calls NVIDIA NIM nemotron-3-ultra-550b-a55b to extract deployment platform resource limits, compute, runtimes, quotas, and credits."""
    prod_list_str = ", ".join([f"'{p}'" for p in target_products])
    content_slice = page_text[:12000]

    system_prompt = (
        "You are an expert cloud infrastructure pricing and quota extractor.\n"
        "Extract free tier / hobby plan limits for the specified products from the documentation.\n"
        "CRITICAL INSTRUCTIONS:\n"
        "1. Extract ONLY from the FREE / FREE TRIAL / HOBBY plan. Do NOT extract limits from paid tiers (such as Pro, Team, or Enterprise).\n"
        "2. PAY CLOSE ATTENTION TO THE PRODUCT NAME AND TYPE:\n"
        "   - If the product specifies Postgres or Database (e.g. 'Render Postgres (Free Plan)'), check if it has a strict expiration or trial period (e.g. Render Postgres expires 30 days after creation -> free_type: 'trial', trial_or_credit_days: 30).\n"
        "   - If the product specifies Web Service or Static Site without expiration, free_type is 'permanent'.\n"
        "   - If a platform has BOTH an introductory one-time trial (e.g. 30-day $5 trial) AND a permanent ongoing free tier/credit (e.g. $1/month ongoing credit), extract the PERMANENT ONGOING FREE TIER limits by default unless the product specifically names a trial.\n"
        "3. Do not confuse transient sandbox or ephemeral demo limits with standard free deployment service limits.\n"
        "Return STRICTLY a valid JSON object with a single key 'products' containing an array of objects:\n"
        "{\n"
        '  "products": [\n'
        '    {\n'
        '      "product_name": "exact or matching product name",\n'
        '      "ram_mb": number or null,\n'
        '      "vcpu": number or null,\n'
        '      "gpu_available": boolean or null,\n'
        '      "execution_model": "always_running" | "scale_to_zero" | "request_scoped" | "static" | "sleeps_after_idle" | "time_limited" | null,\n'
        '      "idle_timeout_min": number or null,\n'
        '      "max_request_timeout_s": number or null,\n'
        '      "bandwidth_gb_month": number or null,\n'
        '      "build_quota": number or null,\n'
        '      "build_quota_unit": "minutes" | "builds" | "hours" | null,\n'
        '      "build_quota_period": "month" | "day" | null,\n'
        '      "requests_quota": number or null,\n'
        '      "requests_period": "month" | "day" | "second" | null,\n'
        '      "persistent_storage_gb": number or null,\n'
        '      "max_projects_or_services": number or null,\n'
        '      "free_type": "permanent" | "trial" | "credit" | "recurring_credit" | "none" | null,\n'
        '      "credit_amount": number or null,\n'
        '      "credit_unit": "usd" | "eur" | "vm_hours" | null,\n'
        '      "credit_period": "month" | "once" | "one_time" | null,\n'
        '      "trial_or_credit_days": number or null\n'
        '    }\n'
        '  ]\n'
        "}\n"
        "Do not include commentary or markdown fences. Return ONLY the JSON object."
    )

    user_prompt = (
        f"Documentation page content:\n{content_slice}\n\n"
        f"Extract free tier compute, runtime, quotas, and credit limits for these deployment products if present: {prod_list_str}."
    )

    raw_content = call_nemotron(system_prompt, user_prompt)
    try:
        parsed = json.loads(raw_content)
        if isinstance(parsed, dict) and "products" in parsed:
            return parsed["products"]
        elif isinstance(parsed, list):
            return parsed
    except Exception as e:
        print(f"[WARN] Failed to parse Deployment Nemotron JSON response: {e}\nRaw output: {raw_content[:300]}")
    return []


def update_last_verified_for_url(csv_path: Path, url: str, new_timestamp: str, url_col_names: list, verified_col_names: list):
    """Updates last verified timestamp for all rows matching the given URL in the CSV."""
    if not csv_path.exists():
        return
        
    with open(csv_path, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
    
    if not reader:
        return
    
    header = reader[0]
    header_lower = [h.strip().lower() for h in header]
    
    url_idx = -1
    for name in url_col_names:
        if name in header_lower:
            url_idx = header_lower.index(name)
            break
            
    ver_idx = -1
    for name in verified_col_names:
        if name in header_lower:
            ver_idx = header_lower.index(name)
            break
            
    if url_idx == -1 or ver_idx == -1:
        return

    norm_target_url = url.strip().split("#")[0].rstrip("/")

    updated_rows = [header]
    for row in reader[1:]:
        if len(row) > url_idx:
            row_url = row[url_idx].strip().split("#")[0].rstrip("/")
            if row_url == norm_target_url:
                while len(row) <= ver_idx:
                    row.append("")
                row[ver_idx] = new_timestamp
        updated_rows.append(row)

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)


def run_llm_monitoring(saved_hashes: dict, current_time_str: str) -> int:
    print(f"\n==================================================")
    print(f"--- Checking Free LLM Offerings Dataset ---")
    print(f"Offering CSV: {LLM_CSV_PATH}")

    if not LLM_CSV_PATH.exists():
        print(f"[WARN] LLM Offerings CSV not found at {LLM_CSV_PATH}")
        return 0

    with open(LLM_CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    url_to_rows = {}
    for row in reader:
        url = (row.get("LIMITS_SOURCE_URL") or row.get("limits_source_url") or "").strip()
        if url and url.lower() not in ["null", "none", "n/a"]:
            url_to_rows.setdefault(url, []).append(row)

    total_changes = 0

    for url, rows in url_to_rows.items():
        print(f"\n[LLM] Checking URL: {url} ({len(rows)} model offerings)")
        try:
            page_text = fetch_url_content(url)
        except Exception as e:
            print(f"[ERROR] Failed to fetch {url}: {e}")
            continue

        new_hash = compute_content_hash(page_text)
        old_hash = saved_hashes.get(url)

        if old_hash is None or old_hash == new_hash:
            if old_hash is None:
                print(f"Initial run for URL. Recorded hash: {new_hash[:12]}...")
                saved_hashes[url] = new_hash
                save_hashes(saved_hashes)
            else:
                print(f"Hash unchanged ({new_hash[:12]}...).")
            update_last_verified_for_url(
                LLM_CSV_PATH, url, current_time_str,
                ["limits_source_url", "limit_source_url"],
                ["limits_last_verified", "limit_last_verified", "last_verified"]
            )
            continue

        # Hash has changed!
        print(f"[CHANGE DETECTED] Page hash changed from {old_hash[:12]}... to {new_hash[:12]}...!")
        target_models = [r.get("MODEL_NAME") or r.get("model_name") for r in rows if r.get("MODEL_NAME") or r.get("model_name")]
        
        print(f"Extracting rate limits via NVIDIA NIM ({MODEL_NAME}) for {len(target_models)} models...")
        try:
            extracted_models = extract_llm_limits_with_nemotron(page_text, target_models)
        except Exception as e:
            print(f"[ERROR] LLM extraction failed: {e}")
            continue

        extracted_lookup = {}
        for em in extracted_models:
            name = (em.get("model_name") or "").lower().strip()
            if name:
                extracted_lookup[name] = em

        url_changes_count = 0
        for r in rows:
            offering_id = r.get("OFFERING_ID") or r.get("offering_id") or ""
            provider_id = r.get("PROVIDER_ID") or r.get("provider_id") or ""
            model_name = r.get("MODEL_NAME") or r.get("model_name") or ""
            norm_model = model_name.lower().strip()

            matched_data = None
            if norm_model in extracted_lookup:
                matched_data = extracted_lookup[norm_model]
            else:
                for em_name, em_val in extracted_lookup.items():
                    if em_name in norm_model or norm_model in em_name:
                        matched_data = em_val
                        break

            if not matched_data:
                continue

            for field in ["RPM", "RPD", "TPM", "TPD"]:
                curr_val_raw = r.get(field) or r.get(field.lower())
                curr_num = parse_numeric_limit(curr_val_raw)
                new_num = parse_numeric_limit(matched_data.get(field.lower()))

                if new_num is not None and curr_num is not None and new_num != curr_num:
                    print(f"  [ALERT] {model_name} {field} changed: {curr_num} -> {new_num}")
                    append_alert(offering_id, provider_id, model_name, url, field, str(curr_num), str(new_num), dataset_type="llm_offering")
                    url_changes_count += 1
                    total_changes += 1

        saved_hashes[url] = new_hash
        save_hashes(saved_hashes)
        update_last_verified_for_url(
            LLM_CSV_PATH, url, current_time_str,
            ["limits_source_url", "limit_source_url"],
            ["limits_last_verified", "limit_last_verified", "last_verified"]
        )
        print(f"Updated hash and last verified timestamp for {url}. Logged {url_changes_count} changes.")

    return total_changes


def run_deployment_monitoring(saved_hashes: dict, current_time_str: str) -> int:
    print(f"\n==================================================")
    print(f"--- Checking Deployment Platforms Offerings Dataset ---")
    print(f"Offering CSV: {DEPLOYMENT_CSV_PATH}")

    if not DEPLOYMENT_CSV_PATH.exists():
        print(f"[WARN] Deployment Offerings CSV not found at {DEPLOYMENT_CSV_PATH}")
        return 0

    with open(DEPLOYMENT_CSV_PATH, "r", encoding="utf-8") as f:
        reader = list(csv.DictReader(f))

    # Group rows by source_url (strip anchor/fragment to avoid redundant fetches)
    url_to_rows = {}
    for row in reader:
        # Ignore empty spacer rows if present in CSV
        if not (row.get("offering_id") or row.get("OFFERING_ID") or row.get("product_name")):
            continue
        url = (row.get("source_url") or row.get("SOURCE_URL") or "").strip()
        if url and url.lower() not in ["null", "none", "n/a"]:
            base_url = url.split("#")[0].rstrip("/")
            url_to_rows.setdefault(base_url, []).append(row)

    total_changes = 0

    for base_url, rows in url_to_rows.items():
        print(f"\n[DEPLOYMENT] Checking URL: {base_url} ({len(rows)} product offerings)")
        try:
            page_text = fetch_url_content(base_url)
        except Exception as e:
            print(f"[ERROR] Failed to fetch {base_url}: {e}")
            continue

        new_hash = compute_content_hash(page_text)
        old_hash = saved_hashes.get(base_url)

        if old_hash is None or old_hash == new_hash:
            if old_hash is None:
                print(f"Initial run for URL. Recorded hash: {new_hash[:12]}...")
                saved_hashes[base_url] = new_hash
                save_hashes(saved_hashes)
            else:
                print(f"Hash unchanged ({new_hash[:12]}...).")
            update_last_verified_for_url(
                DEPLOYMENT_CSV_PATH, base_url, current_time_str,
                ["source_url", "pricing_url", "docs_url"],
                ["last_verified", "limits_last_verified"]
            )
            continue

        # Hash has changed!
        print(f"[CHANGE DETECTED] Page hash changed from {old_hash[:12]}... to {new_hash[:12]}...!")
        target_products = [r.get("product_name") or r.get("offering_id") for r in rows if r.get("product_name") or r.get("offering_id")]

        print(f"Extracting deployment compute/runtime/quota limits via NVIDIA NIM ({MODEL_NAME}) for {len(target_products)} products...")
        try:
            extracted_products = extract_deployment_limits_with_nemotron(page_text, target_products)
        except Exception as e:
            print(f"[ERROR] Deployment LLM extraction failed: {e}")
            continue

        extracted_lookup = {}
        for ep in extracted_products:
            name = (ep.get("product_name") or "").lower().strip()
            if name:
                extracted_lookup[name] = ep

        url_changes_count = 0
        for r in rows:
            offering_id = r.get("offering_id") or ""
            platform_id = r.get("platform_id") or ""
            product_name = r.get("product_name") or offering_id
            norm_name = product_name.lower().strip()

            matched_data = None
            if norm_name in extracted_lookup:
                matched_data = extracted_lookup[norm_name]
            else:
                for ep_name, ep_val in extracted_lookup.items():
                    if ep_name in norm_name or norm_name in ep_name:
                        matched_data = ep_val
                        break

            if not matched_data:
                continue

            # Compare all requested fields
            for field in DEPLOYMENT_MONITORED_FIELDS:
                curr_val = r.get(field)
                new_val = matched_data.get(field)

                if values_differ(curr_val, new_val):
                    print(f"  [ALERT] {product_name} {field} changed: '{curr_val}' -> '{new_val}'")
                    append_alert(
                        offering_id, platform_id, product_name, base_url, field,
                        str(curr_val) if curr_val is not None else "",
                        str(new_val) if new_val is not None else "",
                        dataset_type="deployment_platform"
                    )
                    url_changes_count += 1
                    total_changes += 1

        saved_hashes[base_url] = new_hash
        save_hashes(saved_hashes)
        update_last_verified_for_url(
            DEPLOYMENT_CSV_PATH, base_url, current_time_str,
            ["source_url", "pricing_url", "docs_url"],
            ["last_verified", "limits_last_verified"]
        )
        print(f"Updated hash and last verified timestamp for {base_url}. Logged {url_changes_count} changes.")

    return total_changes


def run_all_workflows():
    print(f"=== Running Limits & Quotas Monitor Workflow for All Datasets ===")
    print(f"Target directory: {TARGET_DIR}")
    saved_hashes = load_hashes()
    current_time_str = datetime.now().astimezone().isoformat()

    llm_alerts = run_llm_monitoring(saved_hashes, current_time_str)
    deployment_alerts = run_deployment_monitoring(saved_hashes, current_time_str)

    total_alerts = llm_alerts + deployment_alerts
    print(f"\n==================================================")
    print(f"Workflow Complete. Total Alerts Generated: {total_alerts}")
    print(f"Alerts logged in: {ALERTS_CSV_PATH}")


if __name__ == "__main__":
    run_all_workflows()
