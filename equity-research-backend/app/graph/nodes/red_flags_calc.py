from typing import List, Dict, Any
from app.schemas.models import FundamentalsSchema

def check_fcf_divergence(fundamentals: FundamentalsSchema) -> Dict[str, Any]:
    """
    Checks if Free Cash Flow is suspiciously lower than Net Income.
    Threshold: FCF < 0.5 * Net Income. (Only flags if Net Income is positive)
    """
    ni = fundamentals.net_income
    fcf = fundamentals.free_cash_flow
    
    if ni is not None and fcf is not None and ni > 0:
        if fcf < (0.5 * ni):
            return {
                "flagged": True,
                "type": "FCF Divergence",
                "severity": "medium",
                "description": f"Free Cash Flow ({fcf:,.0f}) is less than 50% of Net Income ({ni:,.0f}). May indicate low earnings quality."
            }
    return {"flagged": False}

def check_high_leverage(fundamentals: FundamentalsSchema) -> Dict[str, Any]:
    """
    Checks if Debt-to-Equity ratio is excessively high.
    Threshold: Total Debt > 2.0 * Total Equity.
    """
    debt = fundamentals.total_debt
    equity = fundamentals.total_equity
    
    if debt is not None and equity is not None and equity > 0:
        if debt > (2.0 * equity):
            ratio = debt / equity
            return {
                "flagged": True,
                "type": "High Leverage",
                "severity": "high",
                "description": f"Debt-to-Equity ratio is {ratio:.2f}x (Threshold: 2.0x). Balance sheet is highly leveraged."
            }
    return {"flagged": False}

def check_liquidity_risk(fundamentals: FundamentalsSchema) -> Dict[str, Any]:
    """
    Checks if Current Liabilities exceed Current Assets (Negative Working Capital).
    Threshold: Current Assets < Current Liabilities.
    """
    ca = fundamentals.current_assets
    cl = fundamentals.current_liabilities
    
    if ca is not None and cl is not None:
        if ca < cl:
            return {
                "flagged": True,
                "type": "Liquidity Risk",
                "severity": "medium",
                "description": f"Current Liabilities ({cl:,.0f}) exceed Current Assets ({ca:,.0f}). Indicates potential short-term liquidity stress."
            }
    return {"flagged": False}

def compute_deterministic_red_flags(fundamentals: FundamentalsSchema) -> List[Dict[str, Any]]:
    """
    Runs all deterministic forensic checks and returns a list of triggered red flags.
    """
    flags = []
    
    fcf_check = check_fcf_divergence(fundamentals)
    if fcf_check["flagged"]:
        flags.append(fcf_check)
        
    leverage_check = check_high_leverage(fundamentals)
    if leverage_check["flagged"]:
        flags.append(leverage_check)
        
    liquidity_check = check_liquidity_risk(fundamentals)
    if liquidity_check["flagged"]:
        flags.append(liquidity_check)
        
    return flags
