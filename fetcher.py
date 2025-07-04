import os
import json
import requests
from datetime import datetime

# Load your watchlist CIKs
with open("cik_watchlist.json", "r") as f:
    CIK_WATCHLIST = json.load(f)

HEADERS = {
    "User-Agent": "contact@oriadawn.xyz",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

def fetch_watchlist_filings():
    trades = {
        "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in CIK_WATCHLIST},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    for ticker, cik in CIK_WATCHLIST.items():
        cik_str = str(cik).zfill(10)  # SEC expects 10 digits
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent_filings = data.get("filings", {}).get("recent", {})
            form_types = recent_filings.get("form", [])
            accession_numbers = recent_filings.get("accessionNumber", [])
            report_dates = recent_filings.get("reportDate", [])

            for form, accession, report_date in zip(form_types, accession_numbers, report_dates):
                if form != "4":  # Only Form 4 for insider trades
                    continue

                # Dummy amount — replace with real parsing logic if you extract shares
                amount = 1000
                link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/index.htm"

                trades["tickers"][ticker]["buys"] += 1  # For demo, count as buy
                trades["tickers"][ticker]["alerts"].append({
                    "link": link,
                    "date": report_date,
                    "type": "Buy",
                    "amount_buys": amount,
                    "amount_sells": 0
                })

        except Exception as e:
            print(f"Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump(trades, f, indent=4)

    print("✅ Fetched all filings.")

if __name__ == "__main__":
    fetch_watchlist_filings()