from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class FundamentalsSchema(BaseModel):
    ticker: str
    company_name: str
    market_cap: Optional[float] = None
    revenue: Optional[float] = None
    net_income: Optional[float] = None
    total_debt: Optional[float] = None
    total_equity: Optional[float] = None
    free_cash_flow: Optional[float] = None
    operating_cash_flow: Optional[float] = None
    gross_profit: Optional[float] = None
    operating_income: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    beta: Optional[float] = None

class InjectionScreenResult(BaseModel):
    flagged: bool
    matched_patterns: List[str] = Field(default_factory=list)

class DCFScenarioOutput(BaseModel):
    projections: List[float]
    terminal_value: float
    enterprise_value: float
    implied_equity_value: float
    implied_fcf_cagr_5yr: Optional[float] = None
    market_premium_vs_dcf_percent: Optional[float] = None

class DCFValuationSchema(BaseModel):
    wacc: float
    scenarios: Dict[str, DCFScenarioOutput]
    sensitivity_grid: Dict[str, Any]
