from core.data.data_service import MarketDataService
from core.models.asset import Asset
from core.models.portfolio import Portfolio


def test_failed_price_update_keeps_old_price_and_reports_market():
    portfolio = Portfolio()
    asset = Asset("AAPL", 2, 100, "US", current_price=120)
    portfolio.add_asset(asset)
    service = MarketDataService()

    def unavailable_price(_ticker, _market):
        raise ValueError("provider unavailable")

    service.get_price = unavailable_price
    result = service.update_portfolio_prices(portfolio)

    assert result["updated"] == 0
    assert result["failed"] == 1
    assert result["failures"] == [
        {"ticker": "AAPL", "market": "US", "error": "provider unavailable"}
    ]
    assert asset.current_price == 120
