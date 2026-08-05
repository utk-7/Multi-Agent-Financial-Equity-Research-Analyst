import asyncio

from app.graph.nodes.ingestion import run_ingestion_node_async
from app.graph.nodes.red_flags_calc import compute_deterministic_red_flags


async def check():
    for ticker in ["AMZN", "TSLA", "VZ", "T", "F", "GM"]:
        res = await run_ingestion_node_async(ticker)
        fundamentals = res["fundamentals"]
        print(f"\n--- {ticker} ---")
        print("Net Income:", fundamentals.net_income)
        print("Free Cash Flow:", fundamentals.free_cash_flow)

        flags = compute_deterministic_red_flags(fundamentals)
        print("Deterministic Flags:", flags)


if __name__ == "__main__":
    asyncio.run(check())
