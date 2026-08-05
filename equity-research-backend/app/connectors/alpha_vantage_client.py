import os
import httpx
import logging
from app.schemas.models import FundamentalsSchema

logger = logging.getLogger(__name__)

def fetch_alpha_vantage_fundamentals(ticker_symbol: str) -> FundamentalsSchema:
    api_key = os.environ.get("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        logger.error("ALPHA_VANTAGE_API_KEY not set")
        return FundamentalsSchema(ticker=ticker_symbol, company_name=ticker_symbol)

    base_url = "https://www.alphavantage.co/query"
    
    try:
        # Fetch Overview
        overview_resp = httpx.get(f"{base_url}?function=OVERVIEW&symbol={ticker_symbol}&apikey={api_key}", timeout=10)
        overview_data = overview_resp.json()
        
        if not overview_data or "Symbol" not in overview_data:
            logger.error(f"Alpha Vantage Overview failed or rate limited for {ticker_symbol}")
            return FundamentalsSchema(ticker=ticker_symbol, company_name=ticker_symbol)
            
        company_name = overview_data.get("Name", ticker_symbol)
        
        def parse_float(val):
            try:
                if val and val != "None" and val != "-":
                    return float(val)
            except:
                pass
            return None

        market_cap = parse_float(overview_data.get("MarketCapitalization"))
        revenue = parse_float(overview_data.get("RevenueTTM"))
        gross_profit = parse_float(overview_data.get("GrossProfitTTM"))
        beta = parse_float(overview_data.get("Beta"))
        
        # Operating income from margin and revenue
        operating_margin = parse_float(overview_data.get("OperatingMarginTTM"))
        operating_income = None
        if operating_margin is not None and revenue is not None:
            operating_income = operating_margin * revenue

        # Fetch Income Statement for Net Income
        is_resp = httpx.get(f"{base_url}?function=INCOME_STATEMENT&symbol={ticker_symbol}&apikey={api_key}", timeout=10)
        is_data = is_resp.json()
        net_income = None
        if "annualReports" in is_data and is_data["annualReports"]:
            net_income = parse_float(is_data["annualReports"][0].get("netIncome"))

        # Fetch Balance Sheet for Debt, Equity, Assets, Liabilities
        bs_resp = httpx.get(f"{base_url}?function=BALANCE_SHEET&symbol={ticker_symbol}&apikey={api_key}", timeout=10)
        bs_data = bs_resp.json()
        total_debt = None
        total_equity = None
        current_assets = None
        current_liabilities = None
        if "annualReports" in bs_data and bs_data["annualReports"]:
            latest_bs = bs_data["annualReports"][0]
            short_debt = parse_float(latest_bs.get("shortTermDebt")) or 0.0
            long_debt = parse_float(latest_bs.get("longTermDebt")) or 0.0
            total_debt = short_debt + long_debt if (short_debt or long_debt) else None
            
            total_equity = parse_float(latest_bs.get("totalShareholderEquity"))
            current_assets = parse_float(latest_bs.get("totalCurrentAssets"))
            current_liabilities = parse_float(latest_bs.get("totalCurrentLiabilities"))

        # Fetch Cash Flow
        cf_resp = httpx.get(f"{base_url}?function=CASH_FLOW&symbol={ticker_symbol}&apikey={api_key}", timeout=10)
        cf_data = cf_resp.json()
        operating_cash_flow = None
        free_cash_flow = None
        if "annualReports" in cf_data and cf_data["annualReports"]:
            latest_cf = cf_data["annualReports"][0]
            operating_cash_flow = parse_float(latest_cf.get("operatingCashflow"))
            
            capex = parse_float(latest_cf.get("capitalExpenditures"))
            if operating_cash_flow is not None and capex is not None:
                # CapEx might be positive or negative depending on provider, assume we subtract or add correctly.
                # Alpha Vantage usually reports capex as positive if it's an outflow.
                # Let's subtract absolute value of capex.
                free_cash_flow = operating_cash_flow - abs(capex)

        return FundamentalsSchema(
            ticker=ticker_symbol,
            company_name=company_name,
            market_cap=market_cap,
            revenue=revenue,
            net_income=net_income,
            total_debt=total_debt,
            total_equity=total_equity,
            free_cash_flow=free_cash_flow,
            operating_cash_flow=operating_cash_flow,
            gross_profit=gross_profit,
            operating_income=operating_income,
            current_assets=current_assets,
            current_liabilities=current_liabilities,
            beta=beta
        )
    except Exception as e:
        logger.error(f"Alpha Vantage fetch error for {ticker_symbol}: {e}")
        return FundamentalsSchema(ticker=ticker_symbol, company_name=ticker_symbol)
