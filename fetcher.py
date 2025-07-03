import json
import requests
from datetime import datetime

def fetch_watchlist_filings():
    with open('cik_watchlist.json') as f:
        watchlist = json.load(f)

    for _, item in watchlist.items():
        cik = str(item["cik_str"]).zfill(10)  # pad to 10 digits for SEC
        ticker = item["ticker"]

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        headers = {
            "User-Agent": "contact@oriadawn.xyz"  # ✅ replace with yours
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                print(f"✅ Fetched {ticker}: {url}")
                # Save or parse here if needed!
                # For example:
                # with open(f"{ticker}_data.json", "w") as out:
                #     json.dump(response.json(), out, indent=2)
            else:
                print(f"❌ {ticker} failed with {response.status_code}: {url}")

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    print(f"✅ Finished at {datetime.now().isoformat()}")

if __name__ == "__main__":
    fetch_watchlist_filings()