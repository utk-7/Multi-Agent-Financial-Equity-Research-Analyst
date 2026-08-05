from typing import Any, Dict, Optional

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

    gross_margin = safe_divide(fundamentals.gross_profit, fundamentals.revenue)

    operating_margin = safe_divide(fundamentals.operating_income, fundamentals.revenue)

    net_margin = safe_divide(fundamentals.net_income, fundamentals.revenue)

    debt_to_equity = safe_divide(fundamentals.total_debt, fundamentals.total_equity)

    current_ratio = safe_divide(
        fundamentals.current_assets, fundamentals.current_liabilities
    )

    fcf_conversion = safe_divide(fundamentals.free_cash_flow, fundamentals.net_income)

    roe = safe_divide(fundamentals.net_income, fundamentals.total_equity)

    return {
        "gross_margin": gross_margin,
        "operating_margin": operating_margin,
        "net_margin": net_margin,
        "debt_to_equity": debt_to_equity,
        "current_ratio": current_ratio,
        "fcf_conversion": fcf_conversion,
        "roe": roe,
    }
