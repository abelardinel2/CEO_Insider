import requests
import json
from datetime import datetime

SEC_HEADERS = {"User-Agent": "contact@oriadawn.xyz"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers.items():
        cik = details["cik"]
        print(f"Processing {ticker} with CIK {cik}")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            response = requests.get(url, headers=SEC_HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent_filings = data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            accession_numbers = recent_filings.get("accessionNumber", [])
            filing_dates = recent_filings.get("filingDate", [])
            owners = recent_filings.get("primaryIssuerName", [])

            alerts = []
            today = datetime.utcnow().date()

            for form, acc_num, f_date, owner in zip(forms, accession_numbers, filing_dates, owners):
                if form == "4":
                    f_dt = datetime.strptime(f_date, "%Y-%m-%d").date()
                    if (today - f_dt).days <= 7:
                        link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}-index.htm"
                        alert = {
                            "owner": owner or "N/A",
                            "type": "Buy",
                            "amount_buys": 1000,
                            "link": link
                        }
                        if alert not in alerts:
                            alerts.append(alert)

            updated[ticker] = {
                "cik": cik,
                "buys": len(alerts),
                "sells": 0,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with fresh, deduped alerts")