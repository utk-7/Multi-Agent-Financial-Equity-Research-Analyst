import pytest
from app.schemas.models import FundamentalsSchema
from app.graph.nodes.red_flags_calc import (
    check_fcf_divergence,
    check_high_leverage,
    check_liquidity_risk,
    compute_deterministic_red_flags
)

def test_check_fcf_divergence_flagged():
    f = FundamentalsSchema(ticker="TEST", company_name="Test", net_income=100.0, free_cash_flow=40.0)
    res = check_fcf_divergence(f)
    assert res["flagged"] is True
    assert res["type"] == "FCF Divergence"

def test_check_fcf_divergence_not_flagged():
    # FCF is 60 > 50 (50% of 100)
    f = FundamentalsSchema(ticker="TEST", company_name="Test", net_income=100.0, free_cash_flow=60.0)
    res = check_fcf_divergence(f)
    assert res["flagged"] is False

def test_check_high_leverage_flagged():
    # Debt = 250, Equity = 100 -> D/E = 2.5 > 2.0
    f = FundamentalsSchema(ticker="TEST", company_name="Test", total_debt=250.0, total_equity=100.0)
    res = check_high_leverage(f)
    assert res["flagged"] is True
    assert res["type"] == "High Leverage"

def test_check_high_leverage_not_flagged():
    f = FundamentalsSchema(ticker="TEST", company_name="Test", total_debt=150.0, total_equity=100.0)
    res = check_high_leverage(f)
    assert res["flagged"] is False

def test_check_liquidity_risk_flagged():
    # CA = 80, CL = 100 -> CA < CL
    f = FundamentalsSchema(ticker="TEST", company_name="Test", current_assets=80.0, current_liabilities=100.0)
    res = check_liquidity_risk(f)
    assert res["flagged"] is True
    assert res["type"] == "Liquidity Risk"

def test_check_liquidity_risk_not_flagged():
    f = FundamentalsSchema(ticker="TEST", company_name="Test", current_assets=120.0, current_liabilities=100.0)
    res = check_liquidity_risk(f)
    assert res["flagged"] is False

def test_compute_deterministic_red_flags_all():
    f = FundamentalsSchema(
        ticker="TEST", 
        company_name="Test",
        net_income=100.0, free_cash_flow=40.0,       # Flags FCF
        total_debt=300.0, total_equity=100.0,        # Flags Leverage
        current_assets=50.0, current_liabilities=80.0 # Flags Liquidity
    )
    flags = compute_deterministic_red_flags(f)
    assert len(flags) == 3
    types = [flag["type"] for flag in flags]
    assert "FCF Divergence" in types
    assert "High Leverage" in types
    assert "Liquidity Risk" in types

def test_compute_deterministic_red_flags_none():
    f = FundamentalsSchema(
        ticker="TEST", 
        company_name="Test",
        net_income=100.0, free_cash_flow=150.0,
        total_debt=50.0, total_equity=100.0,
        current_assets=200.0, current_liabilities=80.0
    )
    flags = compute_deterministic_red_flags(f)
    assert len(flags) == 0
