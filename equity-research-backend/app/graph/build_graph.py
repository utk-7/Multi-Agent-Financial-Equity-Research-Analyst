import logging
import os

from app.graph.nodes.ingestion import run_ingestion_node_async
from app.graph.nodes.ratio import ratio_node
from app.graph.nodes.red_flag import red_flag_node
from app.graph.nodes.sentiment import sentiment_node
from app.graph.nodes.valuation import valuation_node
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph

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


from app.evals.metrics import compute_eval_metrics
from app.export.markdown_export import export_to_markdown
from app.export.pdf_export import export_to_pdf
from app.graph.nodes.synthesis import synthesis_node as real_synthesis_node
from app.guardrails.citation_check import check_citations


async def synthesis_node(state: AgentState, config: RunnableConfig) -> dict:
    logger.info(f"Running Synthesis Agent for {state.get('ticker')}")

    synth_result = await real_synthesis_node(state, config)
    final_report = synth_result.get("final_report")

    if not final_report:
        return {"final_report": None, "citations": [], "eval_metrics": {}}

    citation_result = await check_citations(final_report, state)

    eval_metrics = compute_eval_metrics(
        total_claims=citation_result.total_claims_checked,
        unsupported_claims=citation_result.unsupported_claims,
    )

    updated_state = {
        **state,
        "final_report": final_report,
        "citations": citation_result.unsupported_claims,
        "eval_metrics": eval_metrics,
    }

    ticker = state.get("ticker", "UNKNOWN")
    output_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output")
    export_to_pdf(updated_state, os.path.join(output_dir, f"{ticker}_report.pdf"))
    export_to_markdown(updated_state, os.path.join(output_dir, f"{ticker}_report.md"))

    logger.info(f"Synthesis Agent completed for {ticker}")
    return {
        "final_report": final_report,
        "citations": citation_result.unsupported_claims,
        "eval_metrics": eval_metrics,
    }


async def human_review_node(state: AgentState, config: RunnableConfig) -> dict:
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

    workflow.add_edge(START, "ingestion")

    workflow.add_edge("ingestion", "ratio")
    workflow.add_edge("ingestion", "sentiment")
    workflow.add_edge("ingestion", "valuation")

    workflow.add_edge("ratio", "fan_in")
    workflow.add_edge("sentiment", "fan_in")
    workflow.add_edge("valuation", "fan_in")

    workflow.add_edge("fan_in", "red_flag")

    workflow.add_conditional_edges(
        "red_flag",
        route_after_red_flag,
        {"human_review": "human_review", "synthesis": "synthesis"},
    )
    workflow.add_edge("human_review", "synthesis")
    workflow.add_edge("synthesis", END)

    memory = MemorySaver()

    return workflow.compile(checkpointer=memory, interrupt_before=["human_review"])
