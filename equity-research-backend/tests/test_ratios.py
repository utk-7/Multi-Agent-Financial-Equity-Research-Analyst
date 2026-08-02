import pytest
from app.schemas.models import FundamentalsSchema
from app.graph.nodes.ratio_calc import compute_ratios

def test_compute_ratios_happy_path():
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        revenue=1000.0,
        gross_profit=400.0,
        operating_income=200.0,
        net_income=100.0,
        total_debt=500.0,
        total_equity=1000.0,
        current_assets=600.0,
        current_liabilities=300.0,
        free_cash_flow=80.0
    )
    
    ratios = compute_ratios(fundamentals)
    
    assert ratios["gross_margin"] == 0.4
    assert ratios["operating_margin"] == 0.2
    assert ratios["net_margin"] == 0.1
    assert ratios["debt_to_equity"] == 0.5
    assert ratios["current_ratio"] == 2.0
    assert ratios["fcf_conversion"] == 0.8
    assert ratios["roe"] == 0.1

def test_compute_ratios_missing_data():
    # Only revenue and net_income are present
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        revenue=1000.0,
        net_income=100.0
    )
    
    ratios = compute_ratios(fundamentals)
    
    assert ratios["net_margin"] == 0.1
    # Everything else should be None because of missing inputs
    assert ratios["gross_margin"] is None
    assert ratios["operating_margin"] is None
    assert ratios["debt_to_equity"] is None
    assert ratios["current_ratio"] is None
    assert ratios["fcf_conversion"] is None
    assert ratios["roe"] is None

def test_compute_ratios_divide_by_zero():
    fundamentals = FundamentalsSchema(
        ticker="TEST",
        company_name="Test Corp",
        revenue=0.0,
        gross_profit=400.0,
        total_equity=0.0,
        total_debt=500.0,
        current_liabilities=0.0,
        current_assets=600.0,
        net_income=0.0,
        free_cash_flow=80.0
    )
    
    ratios = compute_ratios(fundamentals)
    
    # All calculations that divide by revenue (0), equity (0), 
    # liabilities (0), or net_income (0) should yield None gracefully.
    assert ratios["gross_margin"] is None
    assert ratios["net_margin"] is None
    assert ratios["debt_to_equity"] is None
    assert ratios["current_ratio"] is None
    assert ratios["fcf_conversion"] is None
    assert ratios["roe"] is None
