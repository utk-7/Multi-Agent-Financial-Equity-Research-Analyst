import logging
from typing import Dict, Any
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig
from app.graph.nodes.red_flags_calc import compute_deterministic_red_flags

logger = logging.getLogger(__name__)

async def red_flag_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Red-Flag Agent starting for {ticker}")
    
    fundamentals = state.get("fundamentals")
    if not fundamentals:
        logger.warning(f"No fundamentals found for {ticker}. Skipping red flags.")
        return {"red_flags": []}
    
    # Run deterministic checks
    flags = compute_deterministic_red_flags(fundamentals)
    
    logger.info(f"Red-Flag Agent completed for {ticker}. Found {len(flags)} flags.")
    
    return {"red_flags": flags}
