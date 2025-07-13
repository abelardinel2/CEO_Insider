import requests
from datetime import datetime, timedelta

def fetch_recent_form4_urls(cik, days_back=7):
    base = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    headers = {"User-Agent": "insider-alert-script"}
    r = requests.get(base, headers=headers)
    if r.status_code != 200:
        return []

    data = r.json()
    cutoff = (datetime.utcnow() - timedelta(days=days_back)).strftime("%Y-%m-%d")
    urls = []

    for f in data.get("filings", {}).get("recent", {}).get("form", []):
        if f == "4":
            idx = data["filings"]["recent"]["form"].index(f)
            date = data["filings"]["recent"]["filingDate"][idx]
            if date >= cutoff:
                accession = data["filings"]["recent"]["accessionNumber"][idx].replace("-", "")
                urls.append(f"https://www.sec.gov/Archives/edgar/data/{str(cik).lstrip('0')}/{accession}/xslF345X03/doc4.xml")

    return urls
