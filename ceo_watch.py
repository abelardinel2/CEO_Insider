import json
import requests
from datetime import datetime
from parse_form4_xml import parse_form4_xml
from send_telegram import send_alert

HEADERS = {"User-Agent": "OriaDawnBot (contact@oriadawn.xyz)"}

def main():
    with open("watchlist_ciks.json", "r") as f:
        companies = json.load(f)["companies"]

    for company in companies:
        ticker = company["ticker"]
        cik = company["cik"]
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"

        r = requests.get(url, headers=HEADERS)
        if r.status_code != 200:
            print(f"❌ Failed to fetch data for {ticker}")
            continue

        data = r.json()
        recent_forms = data["filings"]["recent"]
        if "4" not in recent_forms["form"]:
            print(f"✅ No recent Form 4 for {ticker}")
            continue

        idx = recent_forms["form"].index("4")
        accession = recent_forms["accessionNumber"][idx].replace("-", "")
        link = f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/primary_doc.xml"

        parsed = parse_form4_xml(link)
        buys, sells, owner = parsed["buys"], parsed["sells"], parsed["owner"]

        if buys == 0 and sells == 0:
            continue

        if sells > 10000:
            bias = "💩🚽 Large Dump"
        elif sells > 0:
            bias = "🔄 Normal Rebalancing"
        elif buys > 0:
            bias = "🤑💰 Insider Accumulating"
        else:
            bias = "❓ Unknown"

        trade_type = "Buy" if buys > 0 else "Sell"
        amount = buys if buys > 0 else sells

        send_alert(ticker, owner, trade_type, amount, bias, link)

if __name__ == "__main__":
    main()
