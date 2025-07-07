import requests
import json

with open("cik_watchlist.json", "r") as f:
    watchlist = json.load(f)

for entry in watchlist:
    cik = entry["cik_str"]
    ticker = entry["ticker"]
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"

    print(f"Fetching {ticker}: {url}")

    try:
        response = requests.get(url, headers={"User-Agent": "OriaDawnBot/1.0"})
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")
        continue

    try:
        index_json = response.json()
        print(f"✅ Fetched: {url}")
    except json.JSONDecodeError:
        print(f"⚠️ Skipping {ticker}: Invalid JSON returned.")
        continue

    # Do something with `index_json` here...
    # Example:
    # print(index_json.keys())