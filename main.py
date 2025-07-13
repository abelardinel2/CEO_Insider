import os
import json
import logging
from datetime import datetime
from fetcher import fetch_form4_urls, parse_form4

# Configure logging to stdout and file
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("bot.log"),
        logging.StreamHandler()
    ]
)

def main():
    # Load environment variables
    telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
    telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not telegram_token or not telegram_chat_id:
        logging.error("Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID")
        return
    
    # Load watchlist
    try:
        with open("cik_watchlist.json", "r") as f:
            watchlist_content = f.read()
            if not watchlist_content.strip():
                logging.error("cik_watchlist.json is empty")
                return
            watchlist = json.loads(watchlist_content)
        
        # Ensure watchlist is a list
        if not isinstance(watchlist, list):
            logging.error(f"cik_watchlist.json is not a list: {watchlist}")
            return
        
        # Validate each item
        for item in watchlist:
            if not isinstance(item, dict) or "ticker" not in item or "cik" not in item:
                logging.error(f"Invalid watchlist item: {item}")
                return
        
    except FileNotFoundError:
        logging.error("cik_watchlist.json not found")
        return
    except json.JSONDecodeError as e:
        logging.error(f"Invalid JSON in cik_watchlist.json: {e}")
        return
    except Exception as e:
        logging.error(f"Error loading cik_watchlist.json: {e}")
        return
    
    # Process each ticker
    for item in watchlist:
        ticker = item["ticker"]
        cik = item["cik"]
        logging.info(f"Scanning {ticker} (CIK: {cik})")
        
        # Fetch Form 4 URLs
        urls = fetch_form4_urls(cik)
        if not urls:
            logging.info(f"No Form 4 URLs found for {ticker}")
            continue
        
        # Parse each Form 4
        for url in urls:
            parse_form4(url, ticker, telegram_token, telegram_chat_id)
        
        # Update alert count
        item["alert_count"] += len(urls)
    
    # Save updated watchlist
    try:
        with open("cik_watchlist.json", "w") as f:
            json.dump(watchlist, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving cik_watchlist.json: {e}")
    
    logging.info(f"Scan completed at {datetime.now()}")

if __name__ == "__main__":
    main()