import json
import requests

# Load watchlist with tickers + CIKs
with open("cik_watchlist.json") as f:
    watchlist = json.load(f)

results = {}

for ticker, info in watchlist["tickers"].items():
    cik = info["cik"]
    print(f"Processing {ticker} with CIK {cik}")

    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"

    headers = {"User-Agent": "contact@oriadawn.xyz"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"✅ Got response for {ticker} ({cik})")
        results[ticker] = info
        results[ticker]["latest_filings"] = response.json()
    else:
        print(f"❌ Error fetching {ticker}: {response.status_code}")

# ✅ Wrap the final output under "tickers"
final_data = {"tickers": results}

with open("insider_flow.json", "w") as f:
    json.dump(final_data, f, indent=2)

print("✅ Wrote insider_flow.json")