import asyncio

import app.connectors.yfinance_client as yfc
import app.graph.nodes.ingestion as ing
from app.graph.nodes.ingestion import run_ingestion_node
from app.schemas.models import FundamentalsSchema
from dotenv import load_dotenv

load_dotenv(override=True)


# Mock yfinance to fail
def mock_fetch_fundamentals(ticker):
    print("Mock yfinance fetch_fundamentals called. Returning empty schema.")
    return FundamentalsSchema(ticker=ticker, company_name=ticker)


ing.fetch_fundamentals = mock_fetch_fundamentals

if __name__ == "__main__":
    print("Testing ingestion fallback with AAPL...")
    result = run_ingestion_node("AAPL")
    fund = result["fundamentals"]
    print("Fundamentals Result:")
    print(fund)

    if fund.market_cap is not None:
        print(
            "\nFallback to Alpha Vantage SUCCESSFUL. Got market cap:", fund.market_cap
        )
    else:
        print("\nFallback to Alpha Vantage FAILED. Market cap is None.")
