import json
import time
from fetcher import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

def load_cik_watchlist():
    with open("cik_watchlist.json") as f:
        return json.load(f)

def main():
    cik_list = load_cik_watchlist()
    for ticker, cik in cik_list.items():
        print(f"🔍 Checking {ticker} (CIK {cik})")
        form4_urls = fetch_recent_form4_urls(cik)

        for url in form4_urls:
            try:
                data = parse_form4_txt(url)
                if not data:
                    continue

                if data["type"] in ["Buy", "Sell"] and data["value"] > 95000:
                    send_alert(
                        ticker=ticker,
                        owner=data["owner"],
                        trade_type=data["type"],
                        amount=data["shares"],
                        bias=data["bias"],
                        link=url,
                    )
            except Exception as e:
                print(f"⚠️ Error processing {url}: {e}")
        time.sleep(1)

if __name__ == "__main__":
    main()