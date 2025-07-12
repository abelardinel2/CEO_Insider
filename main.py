import json
from sec_fetcher import fetch_insider_trades
from parse_form4_txt import parse_form4_txt
from telegram_alert import send_telegram_alert

with open("cik_watchlist.json") as f:
    watchlist = json.load(f)

output = {}

for ticker, info in watchlist["tickers"].items():
    cik = info["cik"]
    trades = fetch_insider_trades(cik)
    buys, sells, alerts = 0, 0, []

    for trade in trades:
        link = trade["linkToTxt"]
        trade_type, amount, price = parse_form4_txt(link)

        if not trade_type or amount == 0:
            continue

        print(f"Parsed: {ticker} | Type: {trade_type} | Amount: {amount} | Price: {price} | Link: {link}")

        # Fallback price if missing
        if not price or float(price) == 0.0:
            price = 1.00

        amount_dollars = float(amount) * float(price)

        # Send alert if total value >= $1 (for now, for testing)
        if amount_dollars >= 1:
            alerts.append({
                "ticker": ticker,
                "trade_type": trade_type,
                "amount": amount,
                "price": price,
                "value": round(amount_dollars, 2),
                "link": link
            })

            if trade_type.lower() == "buy":
                buys += 1
            elif trade_type.lower() == "sell":
                sells += 1

            send_telegram_alert(ticker, trade_type, amount, amount_dollars, link)

    output[ticker] = {
        "cik": cik,
        "buys": buys,
        "sells": sells,
        "alerts": alerts
    }

with open("insider_flow.json", "w") as f:
    json.dump(output, f, indent=2)

print("✅ insider_flow.json saved with", sum(len(v["alerts"]) for v in output.values()), "alerts.")