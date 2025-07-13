import requests

def fetch_recent_form4_urls(cik: str):
    base_url = f"https://data.sec.gov/submissions/CIK{cik.zfill(10)}.json"
    headers = {"User-Agent": "Oria Dawn Analytics contact@oriadawn.xyz"}
    try:
        response = requests.get(base_url, headers=headers)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch submissions for CIK {cik}")
            return []
        data = response.json()
        urls = []
        for idx, form_type in enumerate(data["filings"]["recent"]["form"]):
            if form_type == "4":
                accession = data["filings"]["recent"]["accessionNumber"][idx].replace("-", "")
                primary_doc = data["filings"]["recent"]["primaryDocument"][idx]
                urls.append(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}")
        return urls
    except Exception as e:
        print(f"❌ Exception fetching data: {e}")
        return []
