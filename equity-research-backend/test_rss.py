import asyncio
from app.graph.nodes.sentiment import fetch_news_headlines
import json

async def main():
    headlines = await fetch_news_headlines("AAPL", limit=10)
    print(f"Number of headlines fetched: {len(headlines)}")
    for i, h in enumerate(headlines):
        print(f" {i+1}. {h}")
        
    headlines_text = "\n".join([f"- {h}" for h in headlines])
    prompt = f"""
Analyze the sentiment of the following recent news headlines for the stock ticker AAPL.
Provide a sentiment score from -1.0 (very negative) to 1.0 (very positive), along with a short rationale.
Headlines:
{headlines_text}
"""
    print("\n--- PROMPT TO BE SENT ---")
    print(prompt)

if __name__ == "__main__":
    asyncio.run(main())
