import json
import requests
import time
from bs4 import BeautifulSoup
from parse_form4_txt import parse_form4_txt

headers = {
    "User-Agent": "insider-flow-analyzer",
    "Accept-Encoding": "gzip, deflate",
    "Host": "www.sec.gov"
}

with open("cik_watchlist.json", "r") as f:
    watchlist = json.load(f)["tickers"]

alerts = {}

for ticker, info in watchlist.items():
    cik = str(info["cik"])
    cik_padded = cik.zfill(10)
    print(f"🔍 Checking {ticker} (CIK {cik})")
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&count=40&owner=only"
    res = requests.get(url, headers=headers)
    
    if res.status_code != 200:
        print(f"❌ Could not fetch company page for {ticker}")
        continue

    soup = BeautifulSoup(res.text, "html.parser")
    rows = soup.find_all("tr")

    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        link_cell = cells[1].find("a")
        if not link_cell:
            continue
        href = link_cell.get("href")
        if "Archives" not in href or not href.endswith(".txt"):
            continue
        txt_url = "https://www.sec.gov" + href

        try:
            txt_res = requests.get(txt_url, headers=headers)
            if txt_res.status_code == 200:
                form_data = parse_form4_txt(txt_res.text)
                if form_data:
                    alerts.setdefault(ticker, []).append(form_data)
                    print(f"✅ Alert for {ticker}: {form_data}")
            time.sleep(0.5)
        except Exception as e:
            print(f"❗ Error fetching or parsing Form 4 for {ticker}: {e}")

with open("insider_flow.json", "w") as f:
    json.dump({"tickers": alerts}, f, indent=2)

print("✅ insider_flow.json saved.")