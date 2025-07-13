import json
import os
from fetcher import fetch_recent_form4_urls
from parse_form4_txt import parse_form4_txt
from send_alert import send_alert

def load_watchlist(path="cik_watchlist.json"):
    with open(path, "r") as f:
        return json.load(f)

def save_watchlist(data, path="cik_watchlist.json"):
    with open(path, "w") as f:
        json.dump(data, f, indent=2)

def main():
    data = load_watchlist()
    for ticker, info in data["tickers"].items():
        cik = info["cik"]
        urls = fetch_recent_form4_urls(cik)
        for url in urls:
            if url in info["alerts"]:
                continue
            parsed = parse_form4_txt(url)
            if parsed:
                code = parsed["code"]
                count_key = f"{code}_count"
                if count_key in info:
                    info[count_key] += 1
                info["alerts"].append(url)
                send_alert(ticker, parsed["owner"], parsed["type"], parsed["shares"], parsed["bias"], url)

    save_watchlist(data)

if __name__ == "__main__":
    main()
