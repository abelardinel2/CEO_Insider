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
        logging