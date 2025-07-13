def parse_form4_txt(text):
    try:
        lines = text.splitlines()
        owner = next(line for line in lines if "owner-name" in line).split(">")[1].split("<")[0].strip()
        amount_line = next(line for line in lines if "transactionShares" in line or "shares" in line)
        amount = ''.join(filter(str.isdigit, amount_line))
        transaction_type = "Buy" if "acquisition" in text.lower() else "Sell"
        bias = "Bullish" if transaction_type == "Buy" else "Bearish"

        return {
            "owner": owner,
            "amount": amount,
            "transaction_type": transaction_type,
            "bias": bias
        }
    except Exception as e:
        print(f"⚠️ Parse error: {e}")
        return None