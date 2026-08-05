import json
import logging
import os
from typing import Any, Dict, List

from app.graph.nodes.red_flags_calc import compute_deterministic_red_flags
from app.graph.state import AgentState
from app.utils.llm_pacer import execute_with_pacing
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

FRAUD_PRECEDENT_CONTEXT = """
Historical Fraud Precedent Context:
1. Enron-style: Complex off-balance sheet entities obscuring debt, aggressive revenue recognition, mark-to-market accounting on future hypothetical profits.
2. Wirecard-style: High reported cash balances that don't match cash flow statements, acquiring businesses at high premiums without clear strategic value, related-party transactions.
3. WorldCom-style: Capitalizing operating expenses to artificially inflate net income and assets.
4. Tyco-style: Unjustified loans to executives, undisclosed related-party transactions, aggressive M&A to mask organic growth decline.
"""


class LLMRedFlag(BaseModel):
    flagged: bool = Field(..., description="True if a flag is found, False otherwise")
    type: str = Field(..., description="The category/type of the red flag")
    severity: str = Field(
        ..., description="Severity of the flag: 'low', 'medium', or 'high'"
    )
    description: str = Field(
        ...,
        description="Detailed description citing specific numbers or narrative text",
    )


class RedFlagLLMResult(BaseModel):
    flags: List[LLMRedFlag] = Field(
        ...,
        description="List of red flags derived from reasoning. Return an empty list if none are found.",
    )


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=15, min=30, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Red-Flag LLM call failed (attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep:.2f}s..."
    ),
)
async def _invoke_llm_with_retry(llm_chain, prompt: str) -> RedFlagLLMResult:
    return await execute_with_pacing(llm_chain.ainvoke, prompt)


async def red_flag_node(state: AgentState, config: RunnableConfig) -> Dict[str, Any]:
    ticker = state.get("ticker", "UNKNOWN")
    logger.info(f"Red-Flag Agent starting for {ticker}")

    fundamentals = state.get("fundamentals")
    if not fundamentals:
        logger.warning(f"No fundamentals found for {ticker}. Skipping red flags.")
        return {"red_flags": []}

    det_flags = compute_deterministic_red_flags(fundamentals)
    final_flags = []
    for f in det_flags:
        f["source"] = "deterministic"
        final_flags.append(f)

    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0,
    )
    structured_llm = llm.with_structured_output(RedFlagLLMResult)

    fundamentals_json = fundamentals.model_dump_json(indent=2)
    ratios = state.get("ratios", {})
    det_flags_text = json.dumps(det_flags, indent=2) if det_flags else "None"

    prompt = f"""
You are a forensic accounting AI analyzing {ticker}.
Evaluate the company's financial state against the following historical fraud precedents.
Also review the deterministic red flags already caught by the system.

{FRAUD_PRECEDENT_CONTEXT}

Company Fundamentals:
{fundamentals_json}

Company Ratios:
{json.dumps(ratios, indent=2)}

Deterministic Flags Already Found:
{det_flags_text}

CRITICAL RULES FOR YOUR ANALYSIS:
1. STRICT GROUNDING: You may reference and discuss any ratio or figure that appears directly in the provided fundamentals or ratios data above (e.g., 'the current ratio of 0.89 computed from the ratios data indicates...'). 
2. NO EXTERNAL KNOWLEDGE: Do not estimate, infer, or recall figures from general knowledge (e.g., historical buyback amounts, estimated intangibles), even if they seem plausible or well-known. If a reasoning step would require a fact not present in the input, explicitly state that it cannot be verified from available data rather than supplying an approximate figure.
3. NO ARITHMETIC: Do not perform any new calculations (e.g., computing a percentage, ratio, difference, or sum yourself). Only cite the pre-computed ratios and numbers provided to you. If a metric is missing, do not attempt to calculate it.

Analyze the data and return any ADDITIONAL qualitative or quantitative red flags based on historical fraud precedents.
If there are none, return an empty list. Do not simply restate the deterministic flags unless you are escalating their severity based on a precedent pattern.
"""

    try:
        result: RedFlagLLMResult = await _invoke_llm_with_retry(structured_llm, prompt)
        for flag in result.flags:
            if flag.flagged:
                final_flags.append(
                    {
                        "flagged": True,
                        "type": flag.type,
                        "severity": flag.severity,
                        "description": flag.description,
                        "source": "llm",
                    }
                )
    except Exception as e:
        logger.error(f"Error invoking LLM for red-flags on {ticker}: {e}")

    logger.info(
        f"Red-Flag Agent completed for {ticker}. Found {len(final_flags)} flags."
    )
    return {"red_flags": final_flags}
