import pytest

from core.models.asset import Asset


def test_asset_creation_with_valid_data():
    asset = Asset("AAPL", 10, 100, "US")
    assert asset.ticker == "AAPL"
    assert asset.quantity == 10
    assert asset.buy_price == 100
    assert asset.market == "US"
    assert asset.currency == "USD"

def test_iranian_asset_uses_rial_as_native_quote_currency():
    asset = Asset("وبملت", 10, 5000, "IR")
    assert asset.currency == "IRR"

def test_asset_rejects_negative_quantity():
    with pytest.raises(ValueError):
        Asset("AAPL", -5, 100, "US")

def test_asset_rejects_invalid_market():
    with pytest.raises(ValueError):
        Asset("AAPL", 10, 100, "EU")

def test_asset_rejects_currency_that_does_not_match_market_quote():
    with pytest.raises(ValueError, match="quotes prices in IRR"):
        Asset("وبملت", 10, 5000, "IR", currency="IRT")
