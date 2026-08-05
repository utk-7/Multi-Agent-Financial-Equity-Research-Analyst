import yfinance as yf

for ticker_symbol in ["AAPL", "MSFT", "AMZN"]:
    ticker = yf.Ticker(ticker_symbol)
    info = ticker.info
    print(f"\n==== {ticker_symbol} ====")
    print("info['netIncomeToCommon']:", info.get("netIncomeToCommon"))
    print("info['operatingMargins']:", info.get("operatingMargins"))
    print("info['totalRevenue']:", info.get("totalRevenue"))

    print("\n-- Financials (Income Statement) --")
    fin = ticker.financials
    if not fin.empty:
        try:
            print("Net Income:")
            print(fin.loc["Net Income"].iloc[:2])
        except KeyError:
            print("Net Income not found in financials")

        try:
            print("Operating Income:")
            print(fin.loc["Operating Income"].iloc[:2])
        except KeyError:
            print("Operating Income not found in financials")
