import re

def parse_form4_txt(text):
    trade_data = []

    owner_match = re.search(r'reportingOwnerName:\s*(.*)', text)
    owner = owner_match.group(1).strip() if owner_match else "Unknown"

    transactions = re.findall(
        r'transactionShares:\s*(?P<shares>[\d,\.]+).*?transactionPricePerShare:\s*\$?(?P<price>[\d\.]+).*?transactionAcquiredDisposedCode:\s*(?P<code>[AD])',
        text, re.DOTALL
    )

    for match in transactions:
        shares = float(match[0].replace(',', ''))
        price = float(match[1])
        code = match[2]

        trade_type = 'Buy' if code == 'A' else 'Sale'
        dollar_value = shares * price

        trade_data.append({
            'owner': owner,
            'trade_type': trade_type,
            'amount': shares,
            'price': price,
            'dollar_value': dollar_value
        })

    return trade_data