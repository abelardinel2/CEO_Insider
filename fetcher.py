import logging
import requests
from lxml import etree
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
from datetime import datetime, timedelta

logging.getLogger().setLevel(logging.INFO)

def is_significant_transaction(tx, person, shares_outstanding=1e6):
    role = person.get("title", "").lower()
    if not any(r in role for r in ["ceo", "chief executive", "cfo", "chief financial", "director", "president"]):
        logging.info(f"Filtered non-significant role: {person.get('title')}")
        return False
    
    code = tx.get("code")
    if code not in ["P", "S", "A", "D", "M", "F"]:
        logging.info(f"Filtered non-significant code: {code}")
        return False
    
    try:
        shares = float(tx.get("amount", 0))
        price = float(tx.get("price", 0))
        dollar_value = shares * price if price else 0
        post_shares = float(tx.get("post_shares", 0))
    except (ValueError, TypeError):
        logging.warning(f"Invalid transaction data: {tx}")
        return False
    
    if dollar_value > 100_000 or shares > 10_000:
        return True
    if post_shares > 0 and (shares / post_shares * 100) > 10:
        return True
    
    return False

async def send_telegram_alert(token, chat_id, message):
    for attempt in range(3):
        try:
            bot = Bot(token=token)
            await bot.send_message(chat_id=chat_id, text=message)
            logging.info(f"Sent alert: {message}")
            return True
        except Exception as e:
            logging.warning(f"Telegram retry {attempt+1}/3: {e}")
            await asyncio.sleep(2 ** attempt)
    logging.error(f"Failed to send alert: {message}")
    return False

def fetch_form4_urls(cik, days_back=30):
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb={end_date}&start=0&count=100"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; InsiderBot/1.0; +your.email@example.com)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        logging.info(f"EDGAR response status for CIK {cik}: {response.status_code}")
        logging.debug(f"EDGAR response content for CIK {cik}: {response.text[:500]}...")  # First 500 chars
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [f"https://www.sec.gov{a['href']}" for a in soup.find_all('a', href=True) if 'xslF345X' in a['href']]
        logging.info(f"Found {len(links)} Form 4 URLs for CIK {cik}: