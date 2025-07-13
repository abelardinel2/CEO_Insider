import requests
from bs4 import BeautifulSoup
import time
import logging

# Configure logging
logging.basicConfig(
    filename="edgar_errors.log",
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def parse_form4_txt(url):
    headers = {"User-Agent": "Oria Dawn Analytics contact@oriadawn.xyz"}

    try:
        time.sleep(0.1)  # SEC rate limit: 100ms
        r = requests.get(url, headers=headers, timeout=10)
        r.raise_for_status()
    except Exception as e:
        logging.error(f"Failed to fetch {url}: {str(e)}")
        print(f"❌ Failed to fetch {url}: {e}")
        return []

    soup = BeautifulSoup(r.content, "xml")
    owner_tag = soup.find("rptOwnerName")
    owner = owner_tag.text.strip() if owner_tag else "Unknown"

    transactions = []
    non_deriv_table = soup.find("nonDerivativeTable")
    if not non_deriv_table:
        logging.warning(f"No nonDerivativeTable in {url}")
        print(f"❌ No nonDerivativeTable in {url}")
        return []

    for transaction in non_deriv_table.find_all("nonDerivativeTransaction"):
        code_tag = transaction.find("transactionCode")
        shares_tag = transaction.find("transactionShares")
        price_tag = transaction.find("transactionPricePerShare")

        if not (code_tag and shares_tag and price_tag):
            logging.warning(f"Missing transaction tags in {url}")
            print(f"❌ Missing transaction tags in {url}")
            continue

        code = code_tag.text.strip()
        if code not in ["A", "D"]:
            logging.warning(f"Invalid transaction code {code} in {url}")
            print(f"❌ Invalid transaction code {code} in {url}")
            continue

        try:
            shares = float(shares_tag.text.strip())
            price = float(price_tag.text.strip())
            value = shares * price
            bias = "💰🤑 Significant Accumulation" if code == "A" else "📉 Likely Distribution"
            trade_type = "Buy" if code == "A" else "Sell"

            transactions.append({
                "owner": owner,
                "type": trade_type,
                "shares": shares,
                "price": price,
                "value": value,
                "bias": bias,
            })
        except (ValueError, AttributeError) as e:
            logging.error(f"Failed to parse transaction in {url}: {str(e)}")
            print(f"❌ Failed to parse transaction in {url}: {e}")
            continue

    return transactions