import logging
import os
import json
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from app.utils.llm_pacer import execute_with_pacing

logger = logging.getLogger(__name__)

class CitationCheckResult(BaseModel):
    unsupported_claims: List[str] = Field(..., description="List of factual claims in the report that cannot be traced to the provided data. Return empty list if all claims are supported.")
    total_claims_checked: int = Field(..., description="Total number of factual claims (numbers, ratios, quotes) found and checked.")

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=15, min=30, max=60),
    reraise=True,
    before_sleep=lambda retry_state: logger.warning(
        f"Citation Check LLM call failed (attempt {retry_state.attempt_number}). Retrying in {retry_state.next_action.sleep:.2f}s..."
    )
)
async def _invoke_llm_with_retry(llm_chain, prompt: str) -> CitationCheckResult:
    return await execute_with_pacing(llm_chain.ainvoke, prompt)

async def check_citations(report: Dict[str, Any], state_data: Dict[str, Any]) -> CitationCheckResult:
    """
    Scans the Synthesis output for factual claims and verifies they are traceable to the state data.
    """
    logger.info("Starting citation check on final report")
    
    llm = ChatOpenAI(
        model=os.getenv("LLM_MODEL", "nvidia/nemotron-3-ultra-550b-a55b:free"),
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=os.getenv("OPENROUTER_API_KEY"),
        temperature=0.0
    )
    structured_llm = llm.with_structured_output(CitationCheckResult)
    
    report_json = json.dumps(report, indent=2)
    
    state_to_dump = {}
    for k, v in state_data.items():
        if hasattr(v, "model_dump"):
            state_to_dump[k] = v.model_dump()
        else:
            state_to_dump[k] = v
            
    state_json = json.dumps(state_to_dump, indent=2, default=str)
    
    prompt = f"""
You are a strict compliance and citation checker.
Your task is to review the following Final Report and ensure EVERY factual claim (especially numbers, ratios, financial figures, and specific sentiment quotes) is explicitly supported by the Provided State Data.

Provided State Data:
{state_json}

Final Report:
{report_json}

INSTRUCTIONS:
1. Identify all factual claims in the Final Report (e.g., specific dollar amounts, percentages, ratios, margins, quoted text).
2. For each claim, check if it can be directly traced to the Provided State Data without requiring new math or external knowledge. Note that the report might format numbers differently (e.g., $1.5B vs 1500000000), which is acceptable as long as the underlying value is correct.
3. If a claim is NOT supported by the data, add it to the `unsupported_claims` list along with a brief explanation of why it fails the check.
4. If all claims are supported, return an empty list for `unsupported_claims`.
5. Count the total number of factual claims you checked and provide it in `total_claims_checked`.
"""

    try:
        result: CitationCheckResult = await _invoke_llm_with_retry(structured_llm, prompt)
        logger.info(f"Citation check completed. Checked {result.total_claims_checked} claims. Found {len(result.unsupported_claims)} unsupported.")
        return result
    except Exception as e:
        logger.error(f"Error invoking LLM for citation check: {e}")
        return CitationCheckResult(unsupported_claims=[], total_claims_checked=0)
