import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 OriaBot (contact@oriadawn.xyz)"
}

def parse_form4(index_url):
    print(f"🔍 Parsing: {index_url}")

    try:
        response = requests.get(index_url, headers=HEADERS, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Failed to fetch index: {e}")
        return None

    soup = BeautifulSoup(response.text, "html.parser")
    # 📝 Replace this with your real extraction:
    tables = soup.find_all("table")
    if tables:
        return f"✅ Found Form 4 table at {index_url}"
    else:
        return None