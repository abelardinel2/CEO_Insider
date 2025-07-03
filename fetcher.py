import os
import requests
import xml.etree.ElementTree as ET
import json
from datetime import datetime, timedelta

# ✅ Your watchlist
WATCHLIST = [
    "PFE", "QUBT", "WMT", "JNJ", "COST", "PEP", "XOM", "AGI", "HL", "SILJ", "GLD",
    "IAU", "BAR", "SLV", "WPM", "AG", "B", "XAGUSD", "COIN", "JPM", "IREN", "FPI",
    "LAND", "WELL", "PSA", "O", "SMCI", "NVDA", "IONQ", "RGTI", "ARKQ", "AIQ", "TEM",
    "PLTR", "USO", "XOP", "PHO", "FIW", "XYL", "AWK", "WTRG", "UFO", "RKLB", "ASTS",
    "BTCUSD", "ETHUSD", "XRPUSD", "SUIUSD", "KYMR", "DHR", "RELIANCE"
]

def fetch_and_update_insider_flow():
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=7)  # ✅ 7-day range
    date_format = "%Y%m%d"

    # SEC Atom feed URL
    url = (
        f"https://www.sec.gov/cgi-bin/browse-edgar?"
        f"action=getcurrent&dateb={start_date.strftime(date_format)}"
        f"&datea={end_date.strftime(date_format)}&type=4&owner=include&output=atom"
    )

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "Chrome/91.0.4472.124 (contact@oriadawn.xyz)",
        "Accept": "application/xml"
    }

    trades = {
        "tickers": {ticker: {"buys": 0, "sells": 0, "alerts": []} for ticker in WATCHLIST},
        "last_updated": datetime.utcnow().isoformat() + "Z"
    }

    try:
        print(f"✅ Fetching SEC Atom feed: {url}")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        for item in root.findall('{http://www.w3.org/2005/Atom}entry'):
            try:
                title = item.find('{http://www.w3.org/2005/Atom}title').text
                summary = item.find('{http://www.w3.org/2005/Atom}summary').text
                link_elem = item.find('{http://www.w3.org/2005/Atom}link')
                link = link_elem.attrib.get('href') if link_elem is not None else "N/A"

                for ticker in WATCHLIST:
                    if ticker in (title or "").upper() or ticker in (summary or "").upper():
                        # Dummy parse: replace with real parser if needed
                        buys = 1000
                        sells = 0
                        trades["tickers"][ticker]["buys"] += buys
                        trades["tickers"][ticker]["alerts"].append({
                            "owner": "Insider",
                            "link": link,
                            "date": datetime.utcnow().isoformat().split("T")[0],
                            "type": "Buy",
                            "amount_buys": buys,
                            "amount_sells": sells
                        })
                        print(f"✅ Matched {ticker}: {link}")

            except Exception as e:
                print(f"⚠️ Skipped bad entry: {e}")

    except Exception as e:
        print(f"❌ SEC fetch failed: {e}")

    finally:
        with open("insider_flow.json", "w") as f:
            json.dump(trades, f, indent=2)

        print("✅ insider_flow.json written")
        with open("output.log", "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - Fetch complete\n")

if __name__ == "__main__":
    fetch_and_update_insider_flow()