import os
import json
import requests
from datetime import datetime

def fetch_and_update_insider_flow():
    # Load the JSON watchlist in the new format
    with open("cik_watchlist.json") as f:
        data = json.load(f)
        watchlist = data["tickers"]

    print("✅ Loaded watchlist with", len(watchlist), "tickers")

    # Example loop to show CIKs
    for ticker, entry in watchlist.items():
        cik = entry["cik"]
        print(f"Processing {ticker} with CIK {cik}")

        # 👇 Example: You could fetch filings for this CIK
        # This is a placeholder URL pattern — adjust as needed:
        filings_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&owner=include&count=10"

        headers = {
            "User-Agent": "Oria Dawn Insider Bot (contact@oriadawn.xyz)",
            "Accept": "application/xml"
        }

        try:
            resp = requests.get(filings_url, headers=headers, timeout=10)
            resp.raise_for_status()
            print(f"✅ Got response for {ticker} ({cik})")

            # Here you would parse the XML or RSS content
            # Example placeholder:
            # parsed = parse_form4_xml(resp.text)

            # For now just log:
            print(f"Fetched data length: {len(resp.text)} chars")

        except requests.RequestException as e:
            print(f"❌ Failed to fetch for {ticker}: {e}")

    # Example: Save an updated timestamp file to show that it ran
    result = {
        "last_checked": datetime.utcnow().isoformat() + "Z"
    }
    with open("insider_flow.json", "w") as f:
        json.dump(result, f, indent=2)
    print("✅ Wrote insider_flow.json with timestamp.")

if __name__ == "__main__":
    fetch_and_update_insider_flow()