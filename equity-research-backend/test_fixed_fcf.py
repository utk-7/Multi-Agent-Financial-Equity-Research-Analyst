import asyncio
import json

from app.connectors.yfinance_client import fetch_fundamentals
from app.graph.nodes.red_flags_calc import compute_deterministic_red_flags


def test_fixed_fcf():
    for ticker in ["MSFT", "AAPL"]:
        fundamentals = fetch_fundamentals(ticker)
        print(f"--- {ticker} Corrected Fundamentals ---")
        print(
            f"Operating Cash Flow: {fundamentals.operating_cash_flow:,.0f}"
            if fundamentals.operating_cash_flow
            else "OCF: None"
        )
        print(
            f"Free Cash Flow: {fundamentals.free_cash_flow:,.0f}"
            if fundamentals.free_cash_flow
            else "FCF: None"
        )

        flags = compute_deterministic_red_flags(fundamentals)

        fcf_flags = [f for f in flags if f["type"] == "FCF Divergence"]
        print(f"FCF Divergence Flag Triggered: {len(fcf_flags) > 0}")
        if fcf_flags:
            print("Description:", fcf_flags[0]["description"])

        print("\nAll flags:")
        print(json.dumps(flags, indent=2))
        print("=" * 50 + "\n")


if __name__ == "__main__":
    test_fixed_fcf()
