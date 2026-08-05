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
    wacc = calculate_wacc(fundamentals)
    assert round(wacc, 4) == 0.1059


def test_project_cash_flows():
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        revenue=1000.0,
        free_cash_flow=100.0,  # 10% FCF margin
    )

    base_proj = project_cash_flows(fundamentals, "base")
    assert round(base_proj[0], 2) == 105.0
    assert round(base_proj[-1], 2) == 127.63

    bull_proj = project_cash_flows(fundamentals, "bull")
    assert round(bull_proj[0], 2) == 132.0


def test_calculate_terminal_value():
    final_fcf = 100.0
    wacc = 0.10
    tgr = 0.02
    tv = calculate_terminal_value(final_fcf, wacc, tgr)
    assert round(tv, 2) == 1275.0


def test_calculate_enterprise_value():
    projections = [100.0] * 5
    tv = 1000.0
    wacc = 0.10
    ev = calculate_enterprise_value(projections, tv, wacc)
    assert round(ev, 2) == 1000.0


def test_generate_sensitivity_grid():
    fundamentals = FundamentalsSchema(
        ticker="TEST", company_name="Test Corp", total_debt=200.0
    )
    projections = [100.0] * 5
    base_wacc = 0.10
    base_tgr = 0.02

    grid = generate_sensitivity_grid(fundamentals, base_wacc, base_tgr, projections)
    assert len(grid) == 5
    for wacc_label, tgr_dict in grid.items():
        assert len(tgr_dict) == 5

    base_ev = grid["10.0%"]["2.00%"]["enterprise_value"]
    assert round(base_ev, 2) == 1170.75
    assert round(grid["10.0%"]["2.00%"]["implied_equity_value"], 2) == 970.75
