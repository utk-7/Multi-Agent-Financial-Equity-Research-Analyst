import yfinance as yf
import logging
from app.schemas.models import FundamentalsSchema

logger = logging.getLogger(__name__)

def fetch_fundamentals(ticker_symbol: str) -> FundamentalsSchema:
    try:
        ticker = yf.Ticker(ticker_symbol)
        info = ticker.info
        
        def get_val(keys):
            for k in keys:
                if k in info and info[k] is not None:
                    return info[k]
            return None
            
        company_name = get_val(["shortName", "longName"]) or ticker_symbol
        market_cap = get_val(["marketCap"])
        revenue = get_val(["totalRevenue"])
        net_income = get_val(["netIncomeToCommon"])
        total_debt = get_val(["totalDebt"])
        
        # Fallback to get total equity if not in info
        total_equity = get_val(["totalStockholderEquity", "totalEquity"])
        if total_equity is None:
            try:
                bs = ticker.balance_sheet
                if not bs.empty:
                    # check for common labels
                    for label in ['Stockholders Equity', 'Total Equity Gross Minority Interest', 'Common Stock Equity']:
                        if label in bs.index:
                            total_equity = float(bs.loc[label].iloc[0])
                            break
                    
                    # ultimate fallback: assets - liabilities
                    if total_equity is None and 'Total Assets' in bs.index and 'Total Liabilities Net Minority Interest' in bs.index:
                        total_equity = float(bs.loc['Total Assets'].iloc[0]) - float(bs.loc['Total Liabilities Net Minority Interest'].iloc[0])
            except Exception:
                pass
                
        free_cash_flow = get_val(["freeCashflow"])
        operating_cash_flow = get_val(["operatingCashflow"])
        
        return FundamentalsSchema(
            ticker=ticker_symbol,
            company_name=company_name,
            market_cap=market_cap,
            revenue=revenue,
            net_income=net_income,
            total_debt=total_debt,
            total_equity=total_equity,
            free_cash_flow=free_cash_flow,
            operating_cash_flow=operating_cash_flow
        )
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker_symbol}: {e}")
        return FundamentalsSchema(ticker=ticker_symbol, company_name=ticker_symbol)
