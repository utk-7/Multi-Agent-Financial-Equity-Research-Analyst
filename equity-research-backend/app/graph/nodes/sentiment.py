import logging
import httpx
import xml.etree.ElementTree as ET
from typing import Dict, Any, List
from pydantic import BaseModel, Field
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

class SentimentResult(BaseModel):
    sentiment_score: float = Field(..., description="Overall sentiment score from -1.0 (very negative) to 1.0 (very positive)")
    rationale: str = Field(..., description="A short paragraph explaining the score based on the headlines")
    supporting_headlines: List[str] = Field(..., description="List of headlines that were analyzed")
    call_succeeded: bool = Field(True, description="True if the LLM call was successful, False otherwise")

async def fetch_news_headlines(ticker: str, limit: int = 10) -> List[str]:
    """Fetches recent news headlines for the given ticker via Google News RSS."""
    url = f"https://news.google.com/rss/search?q={ticker}+stock&hl=en-US&gl=US&ceid=US:en"
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(url, timeout=10.0)
            resp.raise_for_status()
            
        root = ET.fromstring(resp.text)
        headlines = []
        for item in root.findall(".//item")[:limit]:
            title = item.findtext("title")
            if title:
                headlines.append(title)
        return headlines
    except Exception as e:
        logger.error(f"Failed to fetch news for {ticker}: {e}")
        return []

from app.utils.llm_pacer import execute_with_pacing

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=15, min=30, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"LLM call failed (attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep:.2f}s..."
    )
)
async def _invoke_llm_with_retry(llm_chain, prompt: str) -> SentimentResult:
    """Invokes the LLM with strict global pacing and exponential backoff."""
    return await execute_with_pacing(llm_chain.ainvoke, prompt)

async def sentiment_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Pulls recent headlines and scores sentiment using OpenRouter."""
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Sentiment Agent starting for {ticker}")
    
    headlines = await fetch_news_headlines(ticker, limit=10)
    
    if not headlines:
        logger.warning(f"No headlines found for {ticker}. Returning neutral sentiment.")
        return {
            "news_sentiment": {
                "sentiment_score": 0.0,
                "rationale": "No recent news headlines found to analyze.",
                "supporting_headlines": [],
                "call_succeeded": True
            }
        }
    
    # Swapped to OpenRouter Llama 3.3 70b Instruct Free Tier
    import os
    from langchain_openai import ChatOpenAI
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "meta-llama/llama-3.3-70b-instruct:free"),
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0
    )
    structured_llm = llm.with_structured_output(SentimentResult)
    
    headlines_text = "\n".join([f"- {h}" for h in headlines])
    prompt = f"""
Analyze the sentiment of the following recent news headlines for the stock ticker {ticker}.
Provide a sentiment score from -1.0 (very negative) to 1.0 (very positive).
You MUST provide a substantive 1-2 sentence rationale explaining your score based on the themes in the headlines.
You MUST list the exact headline titles you used as evidence in the supporting_headlines field. Do not leave it empty.
Headlines:
{headlines_text}
"""
    try:
        result: SentimentResult = await _invoke_llm_with_retry(structured_llm, prompt)
        logger.info(f"Sentiment Agent completed for {ticker}")
        
        out_dict = result.model_dump()
        out_dict["call_succeeded"] = True
        
        return {"news_sentiment": out_dict}
    except Exception as e:
        logger.error(f"Error invoking LLM for sentiment on {ticker}: {e}")
        return {
            "news_sentiment": {
                "sentiment_score": 0.0,
                "rationale": f"Failed to analyze sentiment due to error: {str(e)}",
                "supporting_headlines": headlines,
                "call_succeeded": False
            }
        }
