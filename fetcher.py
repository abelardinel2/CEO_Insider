import json
import requests

# Load your tickers JSON
with open('cik_watchlist.json') as f:
    watchlist = json.load(f)

output = {}

for ticker, info in watchlist["tickers"].items():
    cik = info["cik"]
    print(f"Processing {ticker} with CIK {cik}")

    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    try:
        response = requests.get(url, headers={"User-Agent": "YourName contact@oriadawn.xyz"})
        response.raise_for_status()
        print(f"✅ Got response for {ticker} ({cik})")
        data = response.json()

        output[ticker] = {
            "cik": cik,
            "data": data
        }

    except Exception as e:
        print(f"❌ Error fetching {ticker}: {e}")

# Write the combined insider flow file
with open("insider_flow.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ Wrote insider_flow.json")