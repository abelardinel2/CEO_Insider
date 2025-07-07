import requests
import json

SEC_HEADERS = {"User-Agent": "contact@oriadawn.xyz"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers.items():
        cik = details["cik"]
        print(f"🔍 Processing {ticker} with CIK {cik}")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
        try:
            response = requests.get(url, headers=SEC_HEADERS, timeout=10)
            response.raise_for_status()

            data = response.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accessions = recent.get("accessionNumber", [])
            owners = recent.get("primaryIssuerName", [])

            alerts = []
            seen = set()

            for form, acc_num, owner in zip(forms, accessions, owners):
                if form == "4" and acc_num not in seen:
                    seen.add(acc_num)
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

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated")