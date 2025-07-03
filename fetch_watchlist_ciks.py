import json
import requests

def fetch_ciks():
    with open("watchlist.json", "r") as f:
        tickers = json.load(f)["tickers"]

    url = "https://www.sec.gov/files/company_tickers.json"
    headers = {
        "User-Agent": "OriaDawnBot (contact@oriadawn.xyz)"
    }

    r = requests.get(url, headers=headers)
    company_data = r.json()

    mapped = []
    for entry in company_data.values():
        if entry["ticker"] in tickers:
            mapped.append({
                "ticker": entry["ticker"],
                "cik": str(entry["cik_str"]).zfill(10)
            })

    with open("watchlist_ciks.json", "w") as f:
        json.dump({"companies": mapped}, f, indent=2)

    print(f"✅ Saved {len(mapped)} mapped CIKs to watchlist_ciks.json")

if __name__ == "__main__":
    fetch_ciks()
