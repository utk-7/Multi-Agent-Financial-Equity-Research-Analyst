import logging
from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes.ingestion import run_ingestion_node_async
from app.graph.nodes.ratio import ratio_node
from app.graph.nodes.sentiment import sentiment_node
from app.graph.nodes.valuation import valuation_node
from langchain_core.runnables import RunnableConfig

from app.graph.nodes.red_flag import red_flag_node

logger = logging.getLogger(__name__)

async def ingestion_node(state: AgentState, config: RunnableConfig) -> dict:
    ticker = state["ticker"]
    logger.info(f"Ingestion Agent starting for {ticker}")
    result = await run_ingestion_node_async(ticker)
    logger.info(f"Ingestion Agent completed for {ticker}")
    return result

async def fan_in(state: AgentState, config: RunnableConfig) -> dict:
    logger.info(f"Fan-in completed for {state.get('ticker')}")
    return {}

def build_equity_research_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("ratio", ratio_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("valuation", valuation_node)
    workflow.add_node("fan_in", fan_in)
    workflow.add_node("red_flag", red_flag_node)
    
    # Edges
    workflow.add_edge(START, "ingestion")
    
    # Parallel fan-out
    workflow.add_edge("ingestion", "ratio")
    workflow.add_edge("ingestion", "sentiment")
    workflow.add_edge("ingestion", "valuation")
    
    # Fan-in
    workflow.add_edge("ratio", "fan_in")
    workflow.add_edge("sentiment", "fan_in")
    workflow.add_edge("valuation", "fan_in")
    
    # Run Red-Flag after everything else completes
    workflow.add_edge("fan_in", "red_flag")
    workflow.add_edge("red_flag", END)
    
    return workflow.compile()
