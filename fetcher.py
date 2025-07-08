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
            response = requests.get(url, headers=SEC_HEADERS)
            response.raise_for_status()

            data = response.json()
            recent = data.get("filings", {}).get("recent", {})
            forms = recent.get("form", [])
            accession_numbers = recent.get("accessionNumber", [])
            owners = recent.get("primaryIssuerName", [])

            alerts = []
            for form, acc_num, owner in zip(forms, accession_numbers, owners):
                if form == "4":
                    link = f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc_num.replace('-', '')}/{acc_num}-index.htm"
                    alerts.append({"owner": owner, "link": link})

            updated[ticker] = {"cik": cik, "alerts": alerts}

        except Exception as e:
            print(f"❌ Fetch error: {e}")

    with open("insider_flow.json", "w") as f:
        json.dump({"tickers": updated}, f, indent=2)
    print("✅ insider_flow.json updated")