import logging
from langgraph.graph import StateGraph, START, END
from app.graph.state import AgentState
from app.graph.nodes.ingestion import run_ingestion_node_async
from app.graph.nodes.ratio import ratio_node
from app.graph.nodes.sentiment import sentiment_node
from app.graph.nodes.valuation import valuation_node
from app.graph.nodes.red_flag import red_flag_node
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver

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

async def synthesis_node(state: AgentState, config: RunnableConfig) -> dict:
    logger.info(f"Synthesis Agent completed for {state.get('ticker')}")
    return {}

async def human_review_node(state: AgentState, config: RunnableConfig) -> dict:
    # Passthrough node just to act as an interrupt point
    logger.info(f"Human review completed for {state.get('ticker')}")
    return {}

def route_after_red_flag(state: AgentState) -> str:
    if state.get("run_mode") == "verified":
        return "human_review"
    return "synthesis"

def build_equity_research_graph():
    workflow = StateGraph(AgentState)
    
    workflow.add_node("ingestion", ingestion_node)
    workflow.add_node("ratio", ratio_node)
    workflow.add_node("sentiment", sentiment_node)
    workflow.add_node("valuation", valuation_node)
    workflow.add_node("fan_in", fan_in)
    workflow.add_node("red_flag", red_flag_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("synthesis", synthesis_node)
    
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
    
    # Routing after red_flag
    workflow.add_conditional_edges("red_flag", route_after_red_flag, {"human_review": "human_review", "synthesis": "synthesis"})
    workflow.add_edge("human_review", "synthesis")
    workflow.add_edge("synthesis", END)
    
    # We add a MemorySaver checkpointer to persist state and allow interrupts
    memory = MemorySaver()
    
    # We compile with an interrupt before 'human_review'
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["human_review"]
    )
