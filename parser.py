import json
import requests
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"
}

def parse_urls():
    with open("cik_watchlist.json", "r") as f:
        cik_data = json.load(f)

    urls = []

    for _, info in cik_data.items():
        cik = str(info["cik_str"]).zfill(10)
        ticker = info["ticker"]

        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        print(f"🔍 Checking {ticker}: {url}")

        try:
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            data = response.json()

            recent = data.get("filings", {}).get("recent", {})
            form_types = recent.get("form", [])
            filing_dates = recent.get("filingDate", [])
            accessions = recent.get("accessionNumber", [])

            for idx, form_type in enumerate(form_types):
                if form_type == "4":
                    filing_date = filing_dates[idx]
                    filing_dt = datetime.strptime(filing_date, "%Y-%m-%d").date()
                    today = datetime.utcnow().date()

                    if (today - filing_dt).days <= 7:
                        accession_clean = accessions[idx].replace("-", "")
                        link = (
                            f"https://www.sec.gov/Archives/edgar/data/"
                            f"{int(cik)}/{accession_clean}/{accessions[idx]}-index.htm"
                        )
                        urls.append(link)

        except Exception as e:
            print(f"❌ Error fetching {ticker}: {e}")

    print(f"✅ Found {len(urls)} fresh Form 4s")
    return urls