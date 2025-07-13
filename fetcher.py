import requests

def fetch_recent_form4_urls(cik: str):
    cik = cik.zfill(10)
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    headers = {"User-Agent": "Oria Dawn Analytics contact@oriadawn.xyz"}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print(f"⚠️ Failed to fetch submissions for CIK {cik} — {response.status_code}")
            return []

        data = response.json()
        urls = []
        forms = data.get("filings", {}).get("recent", {}).get("form", [])
        accessions = data.get("filings", {}).get("recent", {}).get("accessionNumber", [])
        docs = data.get("filings", {}).get("recent", {}).get("primaryDocument", [])

        for i, form in enumerate(forms):
            if form == "4" and i < len(accessions) and i < len(docs):
                accession = accessions[i].replace("-", "")
                primary_doc = docs[i]
                if primary_doc.endswith(".xml"):
                    urls.append(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/{primary_doc}")
        return urls

    except Exception as e:
        print(f"❌ Exception while fetching CIK {cik}: {e}")
        return []