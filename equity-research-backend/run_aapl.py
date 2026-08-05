import asyncio
import json

from app.graph.build_graph import build_equity_research_graph
from dotenv import load_dotenv

load_dotenv(override=True)


async def main():
    graph = build_equity_research_graph()
    config = {"configurable": {"thread_id": "test_real_run_aapl"}}
    state = {"ticker": "AAPL", "run_mode": "fast"}

    print("Running graph...")
    result = await graph.ainvoke(state, config=config)

    final_report = result.get("final_report", {})
    eval_metrics = result.get("eval_metrics", {})

    print("\n--- SYNTHESIS OUTPUT ---")
    print(json.dumps(final_report, indent=2))

    print("\n--- EVAL METRICS ---")
    print(json.dumps(eval_metrics, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
