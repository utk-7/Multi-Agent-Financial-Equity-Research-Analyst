import logging
from typing import Any, Dict

from app.graph.nodes.ratio_calc import compute_ratios
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def ratio_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Calculates financial ratios based on ingested fundamentals."""
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Ratio Agent starting for {ticker}")

    fundamentals = state.get("fundamentals")
    if not fundamentals:
        logger.warning(
            f"No fundamentals found in state for {ticker}. Returning empty ratios."
        )
        return {"ratios": {}}

    ratios = compute_ratios(fundamentals)
    logger.info(f"Ratio Agent completed for {ticker}")

    return {"ratios": ratios}
