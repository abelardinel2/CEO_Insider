from fetch_sec_filings import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_telegram import send_alert
import json

with open("cik_watchlist.json") as f:
    watchlist = json.load(f)["tickers"]

try:
    with open("insider_flow.json") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {ticker: {"alerts": []} for ticker in watchlist}

for ticker, info in watchlist.items():
    cik = str(info["cik"])
    urls = fetch_recent_form4_urls(cik, days_back=7)
    for url in urls:
        try:
            result = parse_form4_txt(url)
            if result and result["value"] >= 95000 and url not in data[ticker]["alerts"]:
                send_alert(
                    ticker,
                    result["owner"],
                    result["type"],
                    result["shares"],
                    result["bias"],
                    url,
                )
                data[ticker]["alerts"].append(url)
        except Exception as e:
            print(f"Error parsing {url}: {e}")

with open("insider_flow.json", "w") as f:
    json.dump(data, f, indent=2)
