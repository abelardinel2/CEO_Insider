import os
import json
import requests
from datetime import datetime

def fetch_watchlist_filings():
    headers = {
        "User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"
    }

    # Load your CIK watchlist
    with open("cik_watchlist.json", "r") as f:
        cik_data = json.load(f)

    trades = {
        "tickers": {},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    for _, info in cik_data.items():
        cik = str(info["cik_str"]).zfill(10)
        ticker = info["ticker"]

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"Fetching {ticker}: {url}")

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent = data.get("filings", {}).get("recent", {})
            form_types = recent.get("form", [])

            buys = sells = 0
            alerts = []

            for idx, form_type in enumerate(form_types):
                if form_type == "4":
                    transaction = {
                        "date": recent["filingDate"][idx],
                        "link": f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{recent['accessionNumber'][idx].replace('-', '')}/{recent['accessionNumber'][idx]}-index.htm",
                        "type": "Buy",
                        "amount_buys": 1000,  # Replace with real parsed value if needed
                        "amount_sells": 0
                    }
                    buys += 1
                    alerts.append(transaction)

            trades["tickers"][ticker] = {
                "buys": buys,
                "sells": sells,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump(trades, f, indent=2)
    print("✅ insider_flow.json updated.")

if __name__ == "__main__":
    fetch_watchlist_filings()