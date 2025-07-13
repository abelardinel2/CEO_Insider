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
            logging.info(f"Raw cik_watchlist.json content: {watchlist_content}")
            watchlist = json.loads(watchlist_content)
        
        # Ensure watchlist has 'tickers' key
        if not isinstance(watchlist, dict) or "tickers" not in watchlist:
            logging.error(f"cik_watchlist.json does not have 'tickers' key: {watchlist}")
            return
        
        # Validate tickers
        tickers = watchlist["tickers"]
        if not isinstance(tickers, dict):
            logging.error(f"'tickers' is not a dictionary: {tickers}")
            return
        
        for ticker, data in tickers.items():
            if not isinstance(data, dict) or "cik" not in data or any(k not in data for k in ["P_count", "S_count", "A_count", "D_count", "M_count", "F_count", "alerts"]):
                logging.error(f"Invalid ticker data for {ticker}: {data}")
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
    for ticker, data in watchlist["tickers"].items():
        cik = data["cik"]
        logging.info(f"Scanning {ticker} (CIK: {cik})")
        
        # Fetch Form 4 URLs
        urls = fetch_form4_urls(cik)
        if not urls:
            logging.info(f"No Form 4 URLs found for {ticker}")
            continue
        
        # Parse each Form 4 and update counts/alerts
        for url in urls:
            parse_form4(url, ticker, telegram_token, telegram_chat_id, watchlist["tickers"][ticker])
    
    # Save updated watchlist
    try:
        with open("cik_watchlist.json", "w") as f:
            json.dump(watchlist, f, indent=2)
    except Exception as e:
        logging.error(f"Error saving cik_watchlist.json: {e}")
    
    logging.info(f"Scan completed at {datetime.now()}")

if __name__ == "__main__":
    main()