import requests
import json
from datetime import datetime

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def fetch_and_update_insider_flow(tickers):
    updated = {}
    lookback_days = 14  # <-- ✅ Lookback window

    for ticker, details in tickers["tickers"].items():
        cik = details["cik"]
        print(f"🔍 Processing {ticker} (CIK {cik})")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()

            data = response.json()
            recent_filings = data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            accession_numbers = recent_filings.get("accessionNumber", [])
            filing_dates = recent_filings.get("filingDate", [])
            owners = data.get("name", "Unknown Issuer")

            alerts = []
            today = datetime.utcnow().date()

            for form, acc_num, filing_date in zip(forms, accession_numbers, filing_dates):
                if form == "4":
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    delta_days = (today - filing_dt).days

                    if delta_days <= lookback_days:
                        link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}-index.htm"
                        alert = {
                            "owner": owners,
                            "type": "Unknown",
                            "amount_buys": 0,
                            "link": link
                        }
                        alerts.append(alert)
                        print(f"✅ Found recent Form 4 for {ticker} on {filing_date}")

            updated[ticker] = {
                "cik": cik,
                "buys": len(alerts),
                "sells": 0,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Fetch error for {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with {len(updated)} tickers")