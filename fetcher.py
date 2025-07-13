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

        recent_filings = data.get("filings", {}).get("recent", {})
        forms = recent_filings.get("form", [])
        accessions = recent_filings.get("accessionNumber", [])
        primary_docs = recent_filings.get("primaryDocument", [])

        for idx, form in enumerate(forms):
            if form == "4":
                accession = accessions[idx].replace("-", "")
                primary_doc = primary_docs[idx]
                url = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}"
                urls.append(url)

        return urls

    except Exception as e:
        print(f"❌ Exception fetching data for CIK {cik}: {e}")
        return []