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
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()

            data = response.json()

            alerts = []
            recent_filings = data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            accession_numbers = recent_filings.get("accessionNumber", [])
            owners = recent_filings.get("primaryIssuerName", [])
            filing_dates = recent_filings.get("filingDate", [])

            for form, acc_num, owner, filing_date in zip(forms, accession_numbers, owners, filing_dates):
                if form == "4":
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    today = datetime.utcnow().date()

                    # ✅ Only include Form 4s filed in last 7 days
                    if (today - filing_dt).days <= 7:
                        link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}-index.htm"
                        alert = {
                            "owner": owner,
                            "type": "Buy",
                            "amount_buys": 1000,
                            "link": link
                        }
                        alerts.append(alert)

            updated[ticker] = {
                "cik": cik,
                "buys": len(alerts),
                "sells": 0,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    # ✅ Wrap & write file
    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated with fresh data")