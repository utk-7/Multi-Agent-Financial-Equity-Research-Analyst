import asyncio
import logging
from app.graph.build_graph import build_equity_research_graph
from dotenv import load_dotenv

# Set up detailed timing logs
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s.%(msecs)03d - %(name)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

async def run_for_ticker(ticker: str):
    logger.info(f"========== Starting Graph for {ticker} ==========")
    graph = build_equity_research_graph()
    
    initial_state = {
        "ticker": ticker,
        "run_mode": "fast"
    }
    import uuid
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    
    # Run the graph
    result = await graph.ainvoke(initial_state, config=config)
    logger.info(f"========== Completed Graph for {ticker} ==========")
    
    # Validate populated fields
    ratios = result.get("ratios", {})
    sentiment = result.get("news_sentiment", {})
    dcf = result.get("dcf_valuation", {})
    
    import json
    print(f"\n--- {ticker} Validation ---")
    print(f"Ratios populated: {len(ratios) > 0} (keys: {list(ratios.keys())[:3]}...)")
    print(f"Sentiment populated: {sentiment.get('sentiment_score') is not None}")
    print("Sentiment Output:")
    print(json.dumps(sentiment, indent=2))
    print(f"DCF populated: {dcf.get('wacc') is not None} (WACC: {dcf.get('wacc')})")
    
    red_flags = result.get("red_flags")
    print(f"Red-Flags populated: {red_flags is not None} (Count: {len(red_flags) if red_flags is not None else 0})")
    if red_flags:
        print(json.dumps(red_flags, indent=2))
        
    print("--------------------------\n")

async def main():
    load_dotenv()
    # Test AAPL only as per instruction
    await run_for_ticker("AMZN")

if __name__ == "__main__":
    asyncio.run(main())
