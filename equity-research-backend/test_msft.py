import asyncio
import json
import traceback

from app.graph.build_graph import build_equity_research_graph
from dotenv import load_dotenv

load_dotenv(override=True)


async def main():
    graph = build_equity_research_graph()
    config = {"configurable": {"thread_id": "test_real_run_msft"}}
    state = {"ticker": "MSFT", "run_mode": "fast"}

    print("Running graph for MSFT...")
    try:
        result = await graph.ainvoke(state, config=config)
        print("\n--- SYNTHESIS OUTPUT ---")
        print(json.dumps(result.get("final_report", {}), indent=2))
    except Exception as e:
        print(f"Graph execution failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
