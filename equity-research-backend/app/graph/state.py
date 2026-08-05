from typing import TypedDict, Literal, Optional, List, Dict, Any
from app.schemas.models import FundamentalsSchema, InjectionScreenResult, DCFValuationSchema

class AgentState(TypedDict):
    ticker: str
    run_mode: Literal["fast", "verified"]
    fundamentals: Optional[FundamentalsSchema]
    risk_factors_text: Optional[str]
    mda_text: Optional[str]
    injection_screen_result: Optional[InjectionScreenResult]
    ratios: Optional[Dict[str, Any]]
    news_sentiment: Optional[Dict[str, Any]]
    dcf_valuation: Optional[DCFValuationSchema]
    red_flags: Optional[List[Dict[str, Any]]]
    approval_status: Optional[str]
    citations: Optional[List[str]]
    eval_metrics: Optional[Dict[str, Any]]
    final_report: Optional[Dict[str, Any]]
