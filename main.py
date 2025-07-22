import json
from datetime import datetime, timedelta
from sec_parser import fetch_rss_form4_filings
from telegram_bot import send_telegram_alert

# Your custom ticker–CIK map
CIK_WATCHLIST = {
    "PFE": 78003,
    "QUBT": 1529113,
    "WMT": 104169,
    "JNJ": 314485,
    "COST": 21344,
    "PEP": 77476,
    "XOM": 34088,
    "AGI": 756894,
    "HL": 719413,
    "SILJ": 1167419,
    "GLD": 1045810,
    "IAU": 1278680,
    "BAR": 1471703,
    "SLV": 1649094,
    "WPM": 1724413,
    "AG": 1722810,
    "B": 1318605,
    "XAGUSD": 1463101,
    "COIN": 1682852,
    "JPM": 19617,
    "IREN": 1863095,
    "FPI": 1591670,
    "LAND": 1423689,
    "WELL": 766704,
    "PSA": 1393311,
    "O": 726728,
    "SMCI": 1581046,
    "NVDA": 1045810,
    "IONQ": 1837105,
    "RGTI": 1848763,
    "ARKQ": 1581046,
    "AIQ": 1649094,
    "TEM": 1858681,
    "PLTR": 1739924,
    "USO": 1260990,
    "XOP": 1160308,
    "PHO": 1200375,
    "FIW": 1428720,
    "XYL": 109468,
    "AWK": 1410636,
    "UFO": 1722810,
    "RKLB": 1724413,
    "ASTS": 1812826,
    "KYMR": 1770121,
    "DHR": 313616,
    "RELIANCE": 924291
    # Add remaining tickers as needed
}

def main():
    found_alert = False
    for ticker, cik in CIK_WATCHLIST.items():
        filings = fetch_rss_form4_filings(cik)
        for f in filings:
            filed_date = datetime.strptime(f["filed"], "%Y-%m-%d")
            if filed_date >= datetime.today() - timedelta(days=7):
                found_alert = True
                message = (
                    f"📢 Insider Alert: {ticker}\n"
                    f"👤 Insider: {f['owner']}\n"
                    f"Type: {f['type']}\n"
                    f"Amount: {f['amount']} shares\n"
                    f"Bias: {f['bias']}\n"
                    f"Link: {f['link']}"
                )
                send_telegram_alert(message)

    if not found_alert:
        send_telegram_alert("🔍 No insider alerts found in your custom watchlist.")

if __name__ == "__main__":
    main()