import app.config as config
import pytest
from app.graph.nodes.dcf_calc import (calculate_enterprise_value,
                                      calculate_terminal_value, calculate_wacc,
                                      generate_sensitivity_grid,
                                      perform_dcf_valuation,
                                      project_cash_flows)
from app.schemas.models import FundamentalsSchema


def test_calculate_wacc():
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        market_cap=800.0,
        total_debt=200.0,
        beta=1.5,
    )
    # Ke = 4% + 1.5 * 5.5% = 12.25%
    # Kd = 5% * (1 - 0.21) = 3.95%
    # WACC = (0.8 * 12.25%) + (0.2 * 3.95%) = 9.8% + 0.79% = 10.59%
    wacc = calculate_wacc(fundamentals)
    assert round(wacc, 4) == 0.1059


def test_project_cash_flows():
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        revenue=1000.0,
        free_cash_flow=100.0,  # 10% FCF margin
    )

    # Base: 5% growth, 0 margin impact
    base_proj = project_cash_flows(fundamentals, "base")
    # Year 1 rev: 1050, fcf = 105
    assert round(base_proj[0], 2) == 105.0
    # Year 5 rev: 1000 * (1.05)^5 = 1276.28, fcf = 127.63
    assert round(base_proj[-1], 2) == 127.63

    # Bull: 10% growth, 200bps margin impact (12% margin)
    bull_proj = project_cash_flows(fundamentals, "bull")
    # Year 1 rev: 1100, fcf = 1100 * 0.12 = 132.0
    assert round(bull_proj[0], 2) == 132.0


def test_calculate_terminal_value():
    final_fcf = 100.0
    wacc = 0.10
    tgr = 0.02
    # TV = (100 * 1.02) / (0.10 - 0.02) = 102 / 0.08 = 1275.0
    tv = calculate_terminal_value(final_fcf, wacc, tgr)
    assert round(tv, 2) == 1275.0


def test_calculate_enterprise_value():
    projections = [100.0] * 5
    tv = 1000.0
    wacc = 0.10
    ev = calculate_enterprise_value(projections, tv, wacc)
    # PV of 100/yr for 5 yrs @ 10% = ~379.08
    # PV of TV @ year 5 = 1000 / 1.10^5 = ~620.92
    # Total ~ 1000.0
    assert round(ev, 2) == 1000.0


def test_generate_sensitivity_grid():
    fundamentals = FundamentalsSchema(
        ticker="TEST", company_name="Test Corp", total_debt=200.0
    )
    projections = [100.0] * 5
    base_wacc = 0.10
    base_tgr = 0.02

    grid = generate_sensitivity_grid(fundamentals, base_wacc, base_tgr, projections)
    # Check dimensions
    assert len(grid) == 5
    for wacc_label, tgr_dict in grid.items():
        assert len(tgr_dict) == 5

    # Base cell should match test_calculate_enterprise_value approximately
    base_ev = grid["10.0%"]["2.00%"]["enterprise_value"]
    # tv = 100 * 1.02 / 0.08 = 1275 -> PV(TV) = 791.68, PV(FCF) = 379.08 -> EV = 1170.75
    assert round(base_ev, 2) == 1170.75
    assert round(grid["10.0%"]["2.00%"]["implied_equity_value"], 2) == 970.75
