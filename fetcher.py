import requests
import json

SEC_HEADERS = {"User-Agent": "OriaBot (contact@oriadawn.xyz)"}

def fetch_and_update_insider_flow(tickers):
    updated = {}

    for ticker, details in tickers["tickers"].items():
        cik = details["cik"]
        print(f"🔍 Processing {ticker} (CIK {cik})")

        url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"

        try:
            response = requests.get(url, headers=SEC_HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent_filings = data.get("filings", {}).get("recent", {})
            forms = recent_filings.get("form", [])
            accessions = recent_filings.get("accessionNumber", [])
            owners = recent_filings.get("primaryIssuerName", [])

            alerts = []

            for form, acc, owner in zip(forms, accessions, owners):
                if form == "4":
                    link_txt = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc.replace('-', '')}/{acc}.txt"
                    alert = {
                        "owner": owner,
                        "link": link_txt
                    }
                    alerts.append(alert)

            updated[ticker] = {
                "cik": cik,
                "alerts": alerts
            }

        except Exception as e:
            print(f"❌ Fetch error for {ticker}: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)

    print("✅ insider_flow.json updated")