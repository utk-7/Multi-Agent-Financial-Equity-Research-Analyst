from typing import List, Optional
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
