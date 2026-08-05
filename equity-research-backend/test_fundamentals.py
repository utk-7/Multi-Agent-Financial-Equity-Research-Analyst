import asyncio
from app.connectors.yfinance_client import fetch_fundamentals
from app.graph.nodes.ratio_calc import compute_ratios
from app.graph.nodes.dcf_calc import perform_dcf_valuation

tickers = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]

for ticker in tickers:
    try:
        fund = fetch_fundamentals(ticker)
        print(f"{ticker} Fundamentals fetched.")
        ratios = compute_ratios(fund)
        print(f"{ticker} Ratios computed.")
        dcf = perform_dcf_valuation(fund)
        print(f"{ticker} DCF computed. WACC: {dcf['wacc']}")
    except Exception as e:
        print(f"{ticker} FAILED: {e}")
