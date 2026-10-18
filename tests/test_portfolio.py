import pytest

from core.models.asset import Asset
from core.models.portfolio import Portfolio


def test_add_asset():
    portfolio = Portfolio()
    asset = Asset("AAPL", 10, 100, "US")
    portfolio.add_asset(asset)
    assert asset in portfolio.assets

def test_add_duplicate_asset_raises_error():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US"))
    with pytest.raises(ValueError):
        portfolio.add_asset(Asset("AAPL", 5, 90, "US"))

def test_remove_asset():
    portfolio = Portfolio()
    asset = Asset("AAPL", 10, 100, "US")
    portfolio.add_asset(asset)
    portfolio.remove_asset("AAPL")
    assert asset not in portfolio.assets

def test_remove_asset_with_lowercase_ticker():
    portfolio = Portfolio()
    asset = Asset("AAPL", 10, 100, "US")
    portfolio.add_asset(asset)
    portfolio.remove_asset("aapl")
    assert asset not in portfolio.assets

def test_remove_nonexistent_asset_raises_error():
    portfolio = Portfolio()
    with pytest.raises(ValueError):
        portfolio.remove_asset("AAPL")

def test_calculate_total_value():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US"))
    portfolio.add_asset(Asset("TSLA", 5, 200, "US"))
    assert portfolio.calculate_total_value() == 2000

def test_calculate_cost_basis():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US"))
    portfolio.add_asset(Asset("TSLA", 5, 200, "US"))
    assert portfolio.calculate_cost_basis() == 2000

def test_calculate_profit_loss():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US", current_price=150))
    assert portfolio.calculate_profit_loss() == 500

def test_calculate_return_percentage_for_empty_portfolio():
    portfolio = Portfolio()
    assert portfolio.calculate_return_percentage() == 0

def test_calculate_return_percentage_normal_case():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US", current_price=150))
    assert portfolio.calculate_return_percentage() == 50

def test_risk_check_flags_high_and_ok():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 80, 1, "US"))  
    portfolio.add_asset(Asset("TSLA", 20, 1, "US"))  
    result = portfolio.risk_check()
    levels = {r["ticker"]: r["level"] for r in result}
    assert levels["AAPL"] == "high"
    assert levels["TSLA"] == "ok"

def test_risk_check_flags_warning_and_ok():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 60, 1, "US"))  
    portfolio.add_asset(Asset("TSLA", 40, 1, "US"))  
    result = portfolio.risk_check()
    levels = {r["ticker"]: r["level"] for r in result}
    assert levels["AAPL"] == "warning"
    assert levels["TSLA"] == "ok"

def test_report_structure():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US", current_price=150))
    result = portfolio.report()
    assert result["total_value"] == 1500
    assert result["cost_basis"] == 1000
    assert result["profit_loss"] == 500
    assert result["return_percentage"] == 50
    assert result["assets"][0]["ticker"] == "AAPL"

def test_mixed_currency_report_keeps_currency_amounts_separate():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 10, 100, "US", current_price=150))
    portfolio.add_asset(Asset("وبملت", 2, 5000, "IR", current_price=4000))

    result = portfolio.report()

    assert result["total_value"] is None
    assert result["cost_basis"] is None
    assert result["currencies"]["USD"]["total_value"] == 1500
    assert result["currencies"]["USD"]["cost_basis"] == 1000
    assert result["currencies"]["USD"]["profit_loss"] == 500
    assert result["currencies"]["USD"]["unrealized_return_percentage"] == 50
    assert result["currencies"]["IRR"]["total_value"] == 8000
    assert result["currencies"]["IRR"]["cost_basis"] == 10000
    assert result["currencies"]["IRR"]["profit_loss"] == -2000
    assert result["currencies"]["IRR"]["unrealized_return_percentage"] == -20
    assert result["assets"][0]["currency_weight"] == 100
    assert result["assets"][1]["currency_weight"] == 100

def test_scalar_total_rejects_mixed_currency_amounts():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 1, 100, "US"))
    portfolio.add_asset(Asset("وبملت", 1, 5000, "IR"))

    with pytest.raises(ValueError, match="across currencies"):
        portfolio.calculate_total_value()
