from typing import Dict, Any, Optional
from app.schemas.models import FundamentalsSchema

def compute_ratios(fundamentals: FundamentalsSchema) -> Dict[str, Any]:
    """
    Computes standard financial ratios from a FundamentalsSchema.
    Returns a dictionary of ratio values. Missing or zero-denominator
    inputs will yield None for the respective ratio.
    """
    
    def safe_divide(num: Optional[float], den: Optional[float]) -> Optional[float]:
        if num is None or den is None or den == 0:
            return None
        return num / den

    # 1. Gross Margin = Gross Profit / Revenue
    gross_margin = safe_divide(fundamentals.gross_profit, fundamentals.revenue)
    
    # 2. Operating Margin = Operating Income / Revenue
    operating_margin = safe_divide(fundamentals.operating_income, fundamentals.revenue)
    
    # 3. Net Margin = Net Income / Revenue
    net_margin = safe_divide(fundamentals.net_income, fundamentals.revenue)
    
    # 4. Debt-to-Equity = Total Debt / Total Equity
    debt_to_equity = safe_divide(fundamentals.total_debt, fundamentals.total_equity)
    
    # 5. Current Ratio = Current Assets / Current Liabilities
    current_ratio = safe_divide(fundamentals.current_assets, fundamentals.current_liabilities)
    
    # 6. FCF Conversion = Free Cash Flow / Net Income
    fcf_conversion = safe_divide(fundamentals.free_cash_flow, fundamentals.net_income)
    
    # 7. Return on Equity (ROE) = Net Income / Total Equity
    roe = safe_divide(fundamentals.net_income, fundamentals.total_equity)
    
    return {
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "fcf_conversion": fcf_conversion,
        "roe": roe
    }
