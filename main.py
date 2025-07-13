import json
import requests
import time
from datetime import datetime, timedelta
from telegram import Bot

TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
bot = Bot(token=TELEGRAM_BOT_TOKEN)

def load_watchlist():
    with open("cik_watchlist.json") as f:
        return json.load(f)["tickers"]

def fetch_company_filings(cik):
    url = f"https://data.sec.gov/submissions/CIK{str(cik).zfill(10)}.json"
    headers = {"User-Agent": "insider-bot"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Could not fetch company page for CIK {cik}: {e}")
        return None

def extract_form4_urls(company_data):
    try:
        filings = company_data["filings"]["recent"]
        form_4_indexes = [i for i, f in enumerate(filings["form"]) if f == "4"]
        urls = []
        for i in form_4_indexes:
            accession = filings["accessionNumber"][i].replace("-", "")
            cik = str(company_data["cik"]).zfill(10)
            urls.append(f"https://www.sec.gov/Archives/edgar/data/{int(cik)}/{accession}/index.json")
        return urls
    except KeyError:
        return []

def fetch_form_data(url):
    headers = {"User-Agent": "insider-bot"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        for file in data.get("directory", {}).get("item", []):
            if file["name"].endswith(".xml") and "form4" in file["name"].lower():
                return f"https://www.sec.gov/Archives/edgar/data/{'/'.join(url.split('/')[-3:-1])}/{file['name']}"
    except:
        return None
    return None

def parse_form4(url):
    try:
        response = requests.get(url, headers={"User-Agent": "insider-bot"})
        if response.status_code == 200:
            text = response.text
            if "<transactionShares>" in text and "<transactionPricePerShare>" in text:
                return True
    except:
        pass
    return False

def send_alert(ticker, cik, form_url, insider="Unknown", shares="0", price="Unknown"):
    bias = "💵🚢 Normal Sell" if insider != "Unknown" else "📉⚠️ Possible Dump"
    message = (
        f"📢 Insider Alert: {ticker}\n"
        f"👤 Insider: {insider}\n"
        f"Type: Unknown\n"
        f"Amount: {shares} shares\n"
        f"Bias: {bias}\n"
        f"Link: {form_url}"
    )
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)

def main():
    tickers = load_watchlist()
    alerts = []
    for ticker, data in tickers.items():
        cik = data["cik"]
        print(f"🔍 Checking {ticker} (CIK {cik})")
        company_data = fetch_company_filings(cik)
        if not company_data:
            continue
        form_urls = extract_form4_urls(company_data)
        for url in form_urls:
            form_url = fetch_form_data(url)
            if form_url and parse_form4(form_url):
                send_alert(ticker, cik, form_url)
                alerts.append(form_url)
                break
            time.sleep(0.5)
        time.sleep(1)

    with open("insider_flow.json", "w") as f:
        json.dump({"alerts": alerts}, f, indent=2)
    print("✅ insider_flow.json saved.")

if __name__ == "__main__":
    main()