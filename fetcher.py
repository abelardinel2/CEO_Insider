import json
import requests
from datetime import datetime

# Load CIK map from your local JSON
with open("cik_watchlist.json", "r") as f:
    CIK_WATCHLIST = json.load(f)

HEADERS = {
    "User-Agent": "contact@oriadawn.xyz CEO_InsiderBot/1.0",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

def fetch_and_update_insider_flow():
    trades = {
        "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in CIK_WATCHLIST},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    for ticker, cik in CIK_WATCHLIST.items():
        cik_str = str(cik).zfill(10)
        url = f"https://data.sec.gov/submissions/CIK{cik_str}.json"

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accessions = recent.get("accessionNumber", [])
            report_dates = recent.get("reportDate", [])

            for form, accession, report_date in zip(forms, accessions, report_dates):
                if form != "4":
                    continue

                link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession.replace('-', '')}/index.htm"

                trades["tickers"][ticker]["buys"] += 1  # Simple count — real share parsing later
                trades["tickers"][ticker]["alerts"].append({
                    "link": link,
                    "date": report_date,
                    "type": "Buy",
                    "amount_buys": 1000,  # Placeholder
                    "amount_sells": 0,
                    "owner": "Insider"
                })

                break  # Just 1 new Form 4 per run

        except Exception as e:
            print(f"❌ Error for {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump(trades, f, indent=4)

    print("✅ Insider flow updated")

if __name__ == "__main__":
    fetch_and_update_insider_flow()