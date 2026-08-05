import logging
from typing import Any, Dict

from app.graph.nodes.dcf_calc import perform_dcf_valuation
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig

logger = logging.getLogger(__name__)


async def valuation_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    """Performs DCF valuation based on ingested fundamentals."""
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Valuation Agent starting for {ticker}")

    fundamentals = state.get("fundamentals")
    if not fundamentals:
        logger.warning(
            f"No fundamentals found in state for {ticker}. Returning empty DCF."
        )
        return {"dcf_valuation": {}}

    dcf_result = perform_dcf_valuation(fundamentals)
    logger.info(f"Valuation Agent completed for {ticker}")

    return {"dcf_valuation": dcf_result}
