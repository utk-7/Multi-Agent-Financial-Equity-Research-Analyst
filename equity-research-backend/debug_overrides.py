import asyncio

from app.connectors.yfinance_client import fetch_fundamentals


async def check():
    for ticker in ["AAPL", "MSFT", "AMZN"]:
        fundamentals = fetch_fundamentals(ticker)
        print(f"\n--- {ticker} ---")
        print("Net Income:", fundamentals.net_income)
        print("Operating Income:", fundamentals.operating_income)
        print("Free Cash Flow:", fundamentals.free_cash_flow)


if __name__ == "__main__":
    asyncio.run(check())
