import logging
import requests
from lxml import etree
from bs4 import BeautifulSoup
from telegram import Bot
import asyncio
from datetime import datetime, timedelta

# Configure logging (already set in main.py)
logging.getLogger().setLevel(logging.INFO)

def is_significant_transaction(tx, person, shares_outstanding=1e6):
    """Determine if a transaction is significant based on role, type, and size."""
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
    
    # Significant if >$100,000, >10,000 shares, or >10% ownership change
    if dollar_value > 100_000 or shares > 10_000:
        return True
    if post_shares > 0 and (shares / post_shares * 100) > 10:
        return True
    
    return False

async def send_telegram_alert(token, chat_id, message):
    """Send a Telegram alert with retries."""
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

def fetch_form4_urls(cik, days_back=7):
    """Fetch Form 4 URLs from SEC EDGAR."""
    end_date = datetime.now().strftime("%Y%m%d")
    start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
    url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=4&dateb={end_date}&start=0&count=100"
    
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; InsiderBot/1.0; +your.email@example.com)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [f"https://www.sec.gov{a['href']}" for a in soup.find_all('a', href=True) if 'xslF345X' in a['href']]
        logging.info(f"Found {len(links)} Form 4 URLs for CIK {cik}")
        return links
    except Exception as e:
        logging.error(f"Error fetching Form 4 URLs for CIK {cik}: {e}")
        return []

def parse_form4(url, ticker, token, chat_id, shares_outstanding=1e6):
    """Parse a Form 4 filing and send alerts for significant transactions."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; InsiderBot/1.0; +your.email@example.com)"}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        tree = etree.fromstring(response.content)
        
        # Extract person details
        person = tree.find(".//reportingOwner")
        name = person.find(".//rptOwnerName").text if person.find(".//rptOwnerName") is not None else "Unknown"
        role = person.find(".//title").text.lower() if person.find(".//title") is not None else ""
        
        # Parse non-derivative transactions
        transactions = []
        non_derivative_table = tree.find(".//nonDerivativeTable")
        if non_derivative_table is None:
            logging.info(f"No nonDerivativeTable in {url}")
            return
        
        for tx in non_derivative_table.findall(".//nonDerivativeTransaction"):
            amount = tx.find(".//transactionAmounts/transactionShares/value").text if tx.find(".//transactionAmounts/transactionShares/value") is not None else "0"
            price = tx.find(".//transactionAmounts/transactionPricePerShare/value").text if tx.find(".//transactionAmounts/transactionPricePerShare/value") is not None else "0"
            code = tx.find(".//transactionCode").text if tx.find(".//transactionCode") is not None else ""
            date = tx.find(".//transactionDate/value").text if tx.find(".//transactionDate/value") is not None else ""
            post_shares = tx.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value").text if tx.find(".//postTransactionAmounts/sharesOwnedFollowingTransaction/value") is not None else "0"
            
            tx_data = {
                "code": code,
                "amount": amount,
                "price": price,
                "date": date,
                "post_shares": post_shares
            }
            
            if is_significant_transaction(tx_data, {"title": role}, shares_outstanding):
                tx_type = "Acquired" if code in ["P", "A", "M"] else "Disposed"
                message = (
                    f"Insider Transaction Alert\n"
                    f"Ticker: {ticker}\n"
                    f"Person: {name} ({role})\n"
                    f"Transaction: {tx_type} {amount} shares at ${price}\n"
                    f"Date: {date}\n"
                    f"Ownership: {post_shares} shares"
                )
                asyncio.run(send_telegram_alert(token, chat_id, message))
                transactions.append(tx_data)
        
        logging.info(f"Processed {len(transactions)} significant transactions for {ticker} from {url}")
    except Exception as e:
        logging.error(f"Error parsing {url}: {e}")