import requests
import json
from datetime import datetime, timedelta

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}
DAYS_LOOKBACK = 14  # Only get new filings in the last 14 days

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers["tickers"].items():
        cik = details["cik"]
        print(f"🔍 Checking {ticker} (CIK {cik})")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()

            data = response.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accession_numbers = recent.get("accessionNumber", [])
            owners = recent.get("primaryIssuerName", [])
            filing_dates = recent.get("filingDate", [])

            alerts = []

            for form, acc_num, owner, filed in zip(forms, accession_numbers, owners, filing_dates):
                if form != "4":
                    continue

                filed_date = datetime.strptime(filed, "%Y-%m-%d").date()
                if (datetime.utcnow().date() - filed_date).days > DAYS_LOOKBACK:
                    continue  # Skip old

                link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}.txt"

                # ✅ Dedupe
                if link not in [a["link"] for a in alerts]:
                    alerts.append({
                        "owner": owner,
                        "type": "Unknown",
                        "amount_buys": 0,
                        "link": link
                    })

            updated[ticker] = {
                "cik": cik,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Fetch error for {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)

    print(f"✅ insider_flow.json saved with {sum(len(v['alerts']) for v in updated.values())} alerts.")