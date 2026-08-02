import asyncio
from app.connectors.yfinance_client import fetch_fundamentals
from app.connectors.edgar_client import fetch_10k_text
from app.guardrails.injection_screen import screen_text

async def run_ingestion_node_async(ticker: str) -> dict:
    # Run fetchers concurrently
    fundamentals_task = asyncio.to_thread(fetch_fundamentals, ticker)
    edgar_task = fetch_10k_text(ticker)
    
    fundamentals, (risk_factors, mda) = await asyncio.gather(
        fundamentals_task, 
        edgar_task
    )
    
    # Screen text
    combined_text = f"{risk_factors or ''}\n\n{mda or ''}"
    screen_result = screen_text(combined_text)
    
    if screen_result.flagged:
        risk_factors = "[REDACTED DUE TO PROMPT INJECTION SCREEN]"
        mda = "[REDACTED DUE TO PROMPT INJECTION SCREEN]"
    
    return {
        "fundamentals": fundamentals,
        "risk_factors_text": risk_factors,
        "mda_text": mda,
        "injection_screen_result": screen_result
    }

def run_ingestion_node(ticker: str) -> dict:
    return asyncio.run(run_ingestion_node_async(ticker))
