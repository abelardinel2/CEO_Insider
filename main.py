import requests
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import telegram
import os
from datetime import datetime

# Telegram setup
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')
bot = telegram.Bot(token=BOT_TOKEN)

# Define owned and targeted assets
OWNED_ITEMS = {'PFE', 'QUBT', 'RGTI', 'SILJ', 'SMCI', 'USO', 'VEGI', 'NBIS', 'AGI', 'B', 'BAR', 'BTCI', 'CETH', 'DHR', 'ENPH', 'FPI', 'HL', 'IONQ', 'JNJ', 'LAND', 'MRNA'}
TARGET_ITEMS = {'WMT', 'COST', 'PEP', 'XOM', 'WELL', 'O', 'PSA', 'GLD', 'IAU', 'XAG', 'SLV', 'AEG', 'AG', 'WPM', 'BTCUSD', 'XRPUSD', 'ETHUSD', 'SUIUSD', 'PLTR', 'ARKQ', 'NVDA', 'AIQ', 'TEM', 'RKLB', 'ASTS', 'UFO', 'TSLA', 'RELIANCE', 'SPY', 'XLP', 'PHO', 'FIW', 'CGW', 'VEOEY', 'XYL', 'WTRG', 'AWK', 'XOP'}

# Combine into a full watchlist
WATCHLIST = OWNED_ITEMS.union(TARGET_ITEMS)

def scrape_sec_insider_trades():
    url = "https://www.sec.gov/cgi-bin/current_q?i=csv"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0.4472.124"}
    for attempt in range(3):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            print(f"Fetched data at {datetime.now()}")  # Debug timestamp
            root = ET.fromstring(response.content)
            relevant_trades = {"owned": [], "targeted": []}
            for item in root.findall('{http://www.w3.org/2005/Atom}entry'):
                title = item.find('{http://www.w3.org/2005/Atom}title').text
                summary = item.find('{http://www.w3.org/2005/Atom}summary').text
                link = item.find('{http://www.w3.org/2005/Atom}link')['href']
                for ticker in WATCHLIST:
                    if ticker in title or ticker in summary:
                        trade_date = item.find('{http://www.w3.org/2005/Atom}published').text.split('T')[0]
                        trade_type = "Unknown"
                        if "purchase" in summary.lower():
                            trade_type = "Buy"
                        elif "sale" in summary.lower():
                            trade_type = "Sale"
                        trade_info = f"{ticker}: {trade_type} Filing - {link} on {trade_date}"
                        if ticker in OWNED_ITEMS:
                            relevant_trades["owned"].append(trade_info)
                        elif ticker in TARGET_ITEMS:
                            relevant_trades["targeted"].append(trade_info)
            return relevant_trades
        except requests.exceptions.RequestError as e:
            if attempt == 2:
                return {"owned": [f"SEC connection error after retries: {e}"], "targeted": []}
        except ET.ParseError:
            if attempt == 2:
                return {"owned": ["Error parsing SEC RSS feed after retries"], "targeted": []}
    return {"owned": [], "targeted": []}

def send_telegram_message(message):
    bot.send_message(chat_id=CHAT_ID, text=message)

def main():
    trades = scrape_sec_insider_trades()
    timestamp = datetime.now().strftime("%Y-%m-d %H:%M:%S ET")
    message = f"Insider Trade Alerts ({timestamp}):\n"

    if trades["owned"]:
        message += "For Owned Assets:\n" + "\n".join(trades["owned"]) + "\n"
    else:
        message += "No insider trades detected for owned assets.\n"

    if trades["targeted"]:
        message += "For Acquisition Targets:\n" + "\n".join(trades["targeted"]) + "\n"
    else:
        message += "No insider trades detected for acquisition targets.\n"

    send_telegram_message(message)

if __name__ == "__main__":
    main()
