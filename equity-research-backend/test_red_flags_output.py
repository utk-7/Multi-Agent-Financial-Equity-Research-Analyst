import asyncio
import json
from app.graph.build_graph import build_equity_research_graph
from dotenv import load_dotenv

async def main():
    load_dotenv()
    graph = build_equity_research_graph()
    
    # Run only for MSFT, and we can just print the red flags!
    # To avoid the sentiment API hanging on 429, we just print the red flags output.
    initial_state = {
        "ticker": "MSFT",
        "run_mode": "fast"
    }
    
    print("Running Graph for MSFT (Deterministic Red Flags Test)...")
    # Actually wait, running the graph WILL trigger sentiment node and hang.
    # So I will just invoke the red_flag_node directly with a mocked state!
    from app.graph.nodes.red_flag import red_flag_node
    from app.schemas.models import FundamentalsSchema
    
    mock_state = {
        "ticker": "MSFT",
        "fundamentals": FundamentalsSchema(
            ticker="MSFT",
            company_name="Microsoft",
            net_income=100.0,
            free_cash_flow=40.0, # FCF divergence
            total_debt=300.0,
            total_equity=100.0, # High leverage
            current_assets=50.0,
            current_liabilities=80.0 # Liquidity Risk
        )
    }
    
    print("Testing red_flag_node directly...")
    result = await red_flag_node(mock_state, None)
    
    red_flags = result.get("red_flags")
    print(f"Red-Flags populated: {red_flags is not None} (Count: {len(red_flags) if red_flags is not None else 0})")
    if red_flags:
        print(json.dumps(red_flags, indent=2))
        
if __name__ == "__main__":
    asyncio.run(main())
