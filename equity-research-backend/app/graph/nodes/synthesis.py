import logging
import os
import json
from typing import Dict, Any
from pydantic import BaseModel, Field
from app.graph.state import AgentState
from langchain_core.runnables import RunnableConfig
from tenacity import retry, stop_after_attempt, wait_exponential
from langchain_openai import ChatOpenAI
from app.utils.llm_pacer import execute_with_pacing

logger = logging.getLogger(__name__)

class FinalReport(BaseModel):
    executive_summary: str = Field(..., description="High-level overview of the company's financial health, sentiment, and valuation.")
    bull_case: str = Field(..., description="The most compelling arguments for investing, based strictly on the provided data.")
    bear_case: str = Field(..., description="The most compelling arguments against investing, including valuation risks and red flags.")
    synthesized_view: str = Field(..., description="Final synthesized analysis balancing the bull and bear arguments.")
    disclaimer: str = Field(..., description="Must exactly read: 'This is research synthesis, not investment advice.'")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=15, min=30, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Synthesis LLM call failed (attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep:.2f}s..."
    )
)
async def _invoke_llm_with_retry(llm_chain, prompt: str) -> FinalReport:
    return await execute_with_pacing(llm_chain.ainvoke, prompt)

async def synthesis_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Synthesis Agent starting for {ticker}")
    
    fundamentals = state.get("fundamentals")
    ratios = state.get("ratios", {})
    news_sentiment = state.get("news_sentiment", {})
    dcf_valuation = state.get("dcf_valuation", {})
    red_flags = state.get("red_flags", [])
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.1
    )
    structured_llm = llm.with_structured_output(FinalReport)
    
    fundamentals_json = fundamentals.model_dump_json(indent=2) if fundamentals else "{}"
    ratios_json = json.dumps(ratios, indent=2)
    sentiment_json = json.dumps(news_sentiment, indent=2)
    dcf_json = dcf_valuation.model_dump_json(indent=2) if hasattr(dcf_valuation, "model_dump_json") else json.dumps(dcf_valuation, indent=2)
    red_flags_json = json.dumps(red_flags, indent=2)
    
    prompt = f"""
You are a top-tier financial equity research analyst synthesizing a final report for {ticker}.
Based on the exact data provided below, produce a final investment thesis comprising an executive summary, a bull case, a bear case, and a synthesized view.

Company Fundamentals:
{fundamentals_json}

Company Ratios:
{ratios_json}

News Sentiment:
{sentiment_json}

DCF Valuation (including pre-computed 5-year CAGR and Market Premium/Discount metrics):
{dcf_json}

Approved Red Flags:
{red_flags_json}

CRITICAL RULES FOR YOUR ANALYSIS:
1. STRICT GROUNDING: You may only reference figures, ratios, and facts that appear EXACTLY in the provided data above. 
2. PRE-COMPUTED METRICS: The data now explicitly includes pre-computed derived metrics (like implied 5-year CAGR and market premium/discount vs DCF value). You MAY and SHOULD cite these exact pre-computed figures directly from the data state. If a pre-computed metric is `null`/not present, do not state a value for it — explicitly note it could not be calculated for this scenario, rather than treating a missing value as zero.
3. NO EXTERNAL KNOWLEDGE: Do not estimate or recall figures from general knowledge. Explicitly decline to state anything you cannot trace to the data.
4. NO ARITHMETIC: Do not perform any new calculations whatsoever (e.g., computing percentages, growth rates, ratios, or differences). Only cite the pre-computed metrics provided.
5. DISCLAIMER REQUIRED: Your output must include the disclaimer "This is research synthesis, not investment advice." in the designated field.
"""

    try:
        result: FinalReport = await _invoke_llm_with_retry(structured_llm, prompt)
        report_dict = result.model_dump()
        logger.info(f"Synthesis Agent completed successfully for {ticker}.")
        return {"final_report": report_dict}
    except Exception as e:
        logger.error(f"Error invoking LLM for synthesis on {ticker}: {e}")
        return {"final_report": None}
