import re

def parse_form4_txt(txt):
    try:
        lines = txt.splitlines()

        trade_type = None
        amount = None
        price = None
        owner = None

        for line in lines:
            # Match transaction code
            if 'transactionAcquiredDisposedCode' in line:
                if 'A' in line:
                    trade_type = 'Buy'
                elif 'D' in line:
                    trade_type = 'Sell'

            # Match number of shares
            if 'transactionShares' in line and not amount:
                match = re.search(r'(\d{1,3}(,\d{3})*|\d+)(\.\d+)?', line)
                if match:
                    amount = match.group().replace(',', '')

            # Match price per share
            if 'transactionPricePerShare' in line and not price:
                match = re.search(r'\d+(\.\d+)?', line)
                if match:
                    price = match.group()

            # Match insider's name
            if 'reportingOwnerName' in line and not owner:
                owner = line.split(">")[-2].strip()

        if trade_type and amount and owner:
            return {
                "owner": owner,
                "type": trade_type,
                "amount": int(float(amount)),
                "price": float(price) if price else None
            }

    except Exception as e:
        print(f"Error parsing Form 4 TXT: {e}")

    return None