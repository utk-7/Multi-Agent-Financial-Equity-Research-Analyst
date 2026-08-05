# DCF and WACC Assumptions Configuration

# WACC Inputs
RISK_FREE_RATE = 0.040  # 4.0%
EQUITY_RISK_PREMIUM = 0.055  # 5.5%
COST_OF_DEBT = 0.050  # 5.0%
TAX_RATE = 0.210  # 21.0%

# Default Beta if missing from yfinance
DEFAULT_BETA = 1.0

# Terminal Value
TERMINAL_GROWTH_RATE = 0.025  # 2.5%

# Scenarios (5-year Explicit Forecast)
SCENARIOS = {
    "base": {"revenue_growth": 0.05, "margin_impact": 0.0},  # 5.0%  # 0 bps
    "bull": {"revenue_growth": 0.10, "margin_impact": 0.02},  # 10.0%  # 200 bps
    "bear": {"revenue_growth": 0.02, "margin_impact": -0.02},  # 2.0%  # -200 bps
}

# Sensitivity Grid Dimensions
WACC_VARIATIONS = [-0.01, -0.005, 0.0, 0.005, 0.01]  # +/- 1.0% in 0.5% steps
TGR_VARIATIONS = [-0.005, -0.0025, 0.0, 0.0025, 0.005]  # +/- 0.5% in 0.25% steps
