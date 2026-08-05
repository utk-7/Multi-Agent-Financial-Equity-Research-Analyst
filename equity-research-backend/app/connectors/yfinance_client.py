import logging

import yfinance as yf
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
                    for label in [
                        "Stockholders Equity",
                        "Total Equity Gross Minority Interest",
                        "Common Stock Equity",
                    ]:
                        if label in bs.index:
                            total_equity = float(bs.loc[label].iloc[0])
                            break

                    # ultimate fallback: assets - liabilities
                    if (
                        total_equity is None
                        and "Total Assets" in bs.index
                        and "Total Liabilities Net Minority Interest" in bs.index
                    ):
                        total_equity = float(bs.loc["Total Assets"].iloc[0]) - float(
                            bs.loc["Total Liabilities Net Minority Interest"].iloc[0]
                        )
            except Exception:
                pass

        operating_cash_flow = get_val(["operatingCashflow"])
        free_cash_flow = get_val(["freeCashflow"])

        # Override with statement data for exact period alignment
        try:
            cf = ticker.cashflow
            if not cf.empty:
                ocf_row = (
                    cf.loc["Operating Cash Flow"]
                    if "Operating Cash Flow" in cf.index
                    else None
                )
                capex_row = (
                    cf.loc["Capital Expenditure"]
                    if "Capital Expenditure" in cf.index
                    else None
                )

                if ocf_row is not None:
                    operating_cash_flow = float(ocf_row.iloc[0])
                    # Manual FCF (OCF + CapEx since CapEx is reported as negative)
                    if capex_row is not None:
                        free_cash_flow = float(ocf_row.iloc[0]) + float(
                            capex_row.iloc[0]
                        )
        except Exception:
            pass

        gross_profit = get_val(["grossProfits", "grossProfit"])
        operating_income = get_val(["operatingMargins"])
        if operating_income is not None and revenue is not None:
            # operatingMargins is a percentage, convert to absolute
            operating_income = operating_income * revenue

        # Override with income statement data for exact period alignment
        try:
            fin = ticker.financials
            if not fin.empty:
                if "Net Income" in fin.index:
                    net_income = float(fin.loc["Net Income"].iloc[0])
                if "Operating Income" in fin.index:
                    operating_income = float(fin.loc["Operating Income"].iloc[0])
                if "Gross Profit" in fin.index:
                    gross_profit = float(fin.loc["Gross Profit"].iloc[0])
                if "Total Revenue" in fin.index:
                    revenue = float(fin.loc["Total Revenue"].iloc[0])
        except Exception:
            pass

        current_assets = None
        current_liabilities = None

        try:
            bs = ticker.balance_sheet
            if not bs.empty:
                for label in ["Current Assets", "Total Current Assets"]:
                    if label in bs.index:
                        current_assets = float(bs.loc[label].iloc[0])
                        break
                for label in ["Current Liabilities", "Total Current Liabilities"]:
                    if label in bs.index:
                        current_liabilities = float(bs.loc[label].iloc[0])
                        break
        except Exception:
            pass

        beta = get_val(["beta"])

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
            beta=beta,
        )
    except Exception as e:
        logger.error(f"Error fetching fundamentals for {ticker_symbol}: {e}")
        return FundamentalsSchema(ticker=ticker_symbol, company_name=ticker_symbol)
