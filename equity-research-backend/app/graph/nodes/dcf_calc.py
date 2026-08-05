from typing import Dict, Any, List
from app.schemas.models import FundamentalsSchema
import app.config as config

def calculate_wacc(fundamentals: FundamentalsSchema) -> float:
    """Calculates the Weighted Average Cost of Capital (WACC)."""
    # 1. Cost of Equity (CAPM)
    beta = fundamentals.beta if fundamentals.beta is not None else config.DEFAULT_BETA
    cost_of_equity = config.RISK_FREE_RATE + (beta * config.EQUITY_RISK_PREMIUM)
    
    # 2. Cost of Debt (After tax)
    cost_of_debt_after_tax = config.COST_OF_DEBT * (1 - config.TAX_RATE)
    
    # 3. Capital Structure Weights
    market_cap = fundamentals.market_cap or 0.0
    total_debt = fundamentals.total_debt or 0.0
    total_capital = market_cap + total_debt
    
    if total_capital == 0:
        return cost_of_equity # Fallback if missing data
        
    weight_equity = market_cap / total_capital
    weight_debt = total_debt / total_capital
    
    # 4. WACC
    wacc = (weight_equity * cost_of_equity) + (weight_debt * cost_of_debt_after_tax)
    return wacc

def project_cash_flows(fundamentals: FundamentalsSchema, scenario: str) -> List[float]:
    """
    Projects Free Cash Flow for a 5-year explicit period based on the scenario.
    Simplified approach: Project revenue, apply FCF margin with scenario impact.
    """
    assumptions = config.SCENARIOS.get(scenario, config.SCENARIOS["base"])
    rev_growth = assumptions["revenue_growth"]
    margin_impact = assumptions["margin_impact"]
    
    rev = fundamentals.revenue or 0.0
    fcf = fundamentals.free_cash_flow or 0.0
    
    base_fcf_margin = (fcf / rev) if rev != 0 else 0.0
    projected_fcf_margin = base_fcf_margin + margin_impact
    
    projections = []
    current_rev = rev
    
    for year in range(1, 6):
        current_rev *= (1 + rev_growth)
        proj_fcf = current_rev * projected_fcf_margin
        projections.append(proj_fcf)
        
    return projections

def calculate_terminal_value(final_fcf: float, wacc: float, tgr: float) -> float:
    """Calculates terminal value using the Gordon Growth Model."""
    if wacc <= tgr:
        # Prevent division by zero or negative terminal value due to growth > wacc
        return 0.0
    return (final_fcf * (1 + tgr)) / (wacc - tgr)

def calculate_enterprise_value(projections: List[float], terminal_value: float, wacc: float) -> float:
    """Discounts cash flows and terminal value to present value."""
    ev = 0.0
    for i, cf in enumerate(projections, start=1):
        ev += cf / ((1 + wacc) ** i)
        
    # Discount terminal value from year 5
    pv_tv = terminal_value / ((1 + wacc) ** 5)
    ev += pv_tv
    return ev

def generate_sensitivity_grid(fundamentals: FundamentalsSchema, base_wacc: float, base_tgr: float, projections: List[float]) -> Dict[str, Any]:
    """Generates a 5x5 sensitivity grid varying WACC and TGR, computing Implied Enterprise Value."""
    grid = {}
    
    for wacc_adj in config.WACC_VARIATIONS:
        wacc = base_wacc + wacc_adj
        wacc_label = f"{wacc:.1%}"
        grid[wacc_label] = {}
        
        for tgr_adj in config.TGR_VARIATIONS:
            tgr = base_tgr + tgr_adj
            tgr_label = f"{tgr:.2%}"
            
            final_fcf = projections[-1] if projections else 0.0
            tv = calculate_terminal_value(final_fcf, wacc, tgr)
            ev = calculate_enterprise_value(projections, tv, wacc)
            
            # Simple implication of Equity Value (assuming Cash=0 as a proxy for EV if missing)
            debt = fundamentals.total_debt or 0.0
            implied_equity = ev - debt
            
            grid[wacc_label][tgr_label] = {
                "enterprise_value": ev,
                "implied_equity_value": implied_equity
            }
            
    return grid

def perform_dcf_valuation(fundamentals: FundamentalsSchema) -> Dict[str, Any]:
    """Orchestrates the DCF valuation process."""
    wacc = calculate_wacc(fundamentals)
    
    scenarios_output = {}
    
    for scenario in ["base", "bull", "bear"]:
        projections = project_cash_flows(fundamentals, scenario)
        tv = calculate_terminal_value(projections[-1] if projections else 0.0, wacc, config.TERMINAL_GROWTH_RATE)
        ev = calculate_enterprise_value(projections, tv, wacc)
        
        debt = fundamentals.total_debt or 0.0
        equity_val = ev - debt
        
        # Calculate 5-year CAGR (Current FCF to Year 5 FCF)
        current_fcf = fundamentals.free_cash_flow or 0.0
        cagr_5yr = None
        if current_fcf > 0 and projections and projections[-1] > 0:
            cagr_5yr = (projections[-1] / current_fcf) ** (1/5) - 1
            
        # Calculate Market Premium vs DCF (e.g. 1.3 = market cap is 130% higher than DCF value)
        market_cap = fundamentals.market_cap or 0.0
        market_premium_vs_dcf_percent = None
        if equity_val > 0:
            market_premium_vs_dcf_percent = (market_cap / equity_val) - 1
        
        scenarios_output[scenario] = {
            "projections": projections,
            "terminal_value": tv,
            "enterprise_value": ev,
            "implied_equity_value": equity_val,
            "implied_fcf_cagr_5yr": cagr_5yr,
            "market_premium_vs_dcf_percent": market_premium_vs_dcf_percent
        }
        
    # Grid using base scenario projections
    base_projections = scenarios_output["base"]["projections"]
    sensitivity_grid = generate_sensitivity_grid(fundamentals, wacc, config.TERMINAL_GROWTH_RATE, base_projections)
    
    return {
        "wacc": wacc,
        "scenarios": scenarios_output,
        "sensitivity_grid": sensitivity_grid
    }
