import json
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"}

def parse_urls():
    with open("cik_watchlist.json") as f:
        cik_data = json.load(f)

    urls = []

    for _, info in cik_data.items():
        cik = str(info["cik"]).zfill(10)
        ticker = info.get("ticker", "Unknown")
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"🔍 Checking {ticker}: {url}")
        response = requests.get(url, headers=HEADERS)
        if response.ok:
            print(f"✅ {ticker} OK")
    return urls