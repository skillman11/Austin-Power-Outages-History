import requests
import json
import os
from datetime import datetime, timezone

# Austin Energy's Kubra API identifiers
INSTANCE_ID = "dd9c446f-f6b8-43f9-8f80-83f5245c60a1"
VIEW_ID = "76446308-a901-4fa3-849c-3dd569933a51"

BASE_URL = "https://kubra.io"

def get(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    resp = requests.get(url, headers=headers, timeout=30)
    resp.raise_for_status()
    return resp.json()

def main():
    timestamp = datetime.now(timezone.utc)
    print(f"Scraping at {timestamp.isoformat()}")

    # Step 1: Get current state to find the data path
    state = get(f"{BASE_URL}/stormcenter/api/v1/stormcenters/{INSTANCE_ID}/views/{VIEW_ID}/currentState?preview=false")
    interval_path = state.get("data", {}).get("interval_generation_data")

    snapshot = {"current_state": state}

    if interval_path:
        # Step 2: Get the summary data which has outage counts
        try:
            summary = get(f"{BASE_URL}/{interval_path}/public/summary-1/data.json")
            snapshot["summary"] = summary
            print(f"Got summary data")
        except Exception as e:
            print(f"Could not get summary: {e}")

        # Step 3: Get the detailed outage report with locations
        try:
            report = get(f"{BASE_URL}/{interval_path}/public/report.json")
            snapshot["report"] = report
            print(f"Got report data")
        except Exception as e:
            print(f"Could not get report: {e}")

        # Step 4: Get service territory outage data
        try:
            thematic = get(f"{BASE_URL}/{interval_path}/public/thematic-1/data.json")
            snapshot["thematic"] = thematic
            print(f"Got thematic data")
        except Exception as e:
            print(f"Could not get thematic: {e}")

    # Save snapshot - one file per day, one record per line
    os.makedirs("data", exist_ok=True)
    date_str = timestamp.strftime("%Y-%m-%d")
    filepath = f"data/{date_str}.jsonl"
    with open(filepath, "a") as f:
        f.write(json.dumps({"timestamp": timestamp.isoformat(), "snapshot": snapshot}) + "\n")
    print(f"Saved to {filepath}")

if __name__ == "__main__":
    main()
