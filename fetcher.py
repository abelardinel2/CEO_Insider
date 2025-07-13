import requests
from datetime import datetime, timedelta

def fetch_recent_form4_urls(cik):
    end = datetime.today()
    start = end - timedelta(days=7)
    url = (
        f"https://efts.sec.gov/LATEST/search-index"
        f"?keys={cik}&startdt={start.strftime('%Y-%m-%d')}"
        f"&enddt={end.strftime('%Y-%m-%d')}&category=form4"
    )

    headers = {"User-Agent": "insider-bot"}
    r = requests.get(url, headers=headers)

    if r.status_code != 200:
        print(f"❌ Error fetching form 4s for CIK {cik}: {r.status_code}")
        return []

    data = r.json()
    urls = []

    for item in data.get("hits", {}).get("hits", []):
        accession = item["_id"].replace("-", "")
        urls.append(f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/xslF345X03/doc1.xml")

    return urls