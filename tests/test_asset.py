import pytest

from core.models.asset import Asset


def test_asset_creation_with_valid_data():
    asset = Asset("AAPL", 10, 100, "US")
    assert asset.ticker == "AAPL"
    assert asset.quantity == 10
    assert asset.buy_price == 100
    assert asset.market == "US"

def test_asset_rejects_negative_quantity():
    with pytest.raises(ValueError):
        Asset("AAPL", -5, 100, "US")

def test_asset_rejects_invalid_market():
    with pytest.raises(ValueError):
        Asset("AAPL", 10, 100, "EU")
