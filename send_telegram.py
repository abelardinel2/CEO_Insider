def send_alert(result: dict):
    message = (
        f"📈 Insider Flow Alert\n"
        f"Date: {result['date']}\n"
        f"Buys: {result['buys_shares']} shares (${result['buys_value']:,.2f})\n"
        f"Sells: {result['sells_shares']} shares (${result['sells_value']:,.2f})\n"
        f"Net: {result['net_shares']} shares (${result['net_value']:,.2f})"
    )
    print(f"📣 Sending to Telegram:\n{message}")
    # Here you’d do your real bot.send_message...