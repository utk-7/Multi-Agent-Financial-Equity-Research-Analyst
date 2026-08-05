import yfinance as yf

for ticker in ["MSFT", "AAPL"]:
    stock = yf.Ticker(ticker)
    info = stock.info
    cf = stock.cashflow

    print(f"--- {ticker} ---")
    print(f"info['operatingCashflow']: {info.get('operatingCashflow')}")
    print(f"info['freeCashflow']: {info.get('freeCashflow')}")
    print(f"info['revenue']: {info.get('totalRevenue')}")

    if not cf.empty:
        # Check cash flow statement rows
        ocf_row = (
            cf.loc["Operating Cash Flow"] if "Operating Cash Flow" in cf.index else None
        )
        capex_row = (
            cf.loc["Capital Expenditure"] if "Capital Expenditure" in cf.index else None
        )
        fcf_row = cf.loc["Free Cash Flow"] if "Free Cash Flow" in cf.index else None

        print(
            "\nCash Flow Statement Latest Column (Index: ",
            cf.columns[0] if len(cf.columns) > 0 else "None",
            ")",
        )
        if ocf_row is not None:
            print(f"OCF: {ocf_row.iloc[0]}")
        if capex_row is not None:
            print(f"CapEx: {capex_row.iloc[0]}")
        if fcf_row is not None:
            print(f"FCF: {fcf_row.iloc[0]}")

        # Calculate manually
        if ocf_row is not None and capex_row is not None:
            print(
                f"Manual FCF (OCF + CapEx since CapEx is negative): {ocf_row.iloc[0] + capex_row.iloc[0]}"
            )

    print("=" * 40 + "\n")
