from models.asset import Asset
from models.portfolio import Portfolio
from services.market_data import MarketDataService

portfolio = Portfolio()
market_data_service = MarketDataService()

a1 = Asset("AAPL", 10, 100)
a2 = Asset("TSLA", 5, 200)
a3 = Asset("NVDA", 20, 150)
a4 = Asset("ABC123", 10, 70)

for asset in [a1, a2, a3, a4]:
    try:
        portfolio.add_asset(asset)
    except ValueError as e:
        print(e)

print("=== BEFORE UPDATE ===")
portfolio.report()

result = market_data_service.update_portfolio_prices(portfolio)
print(f"Updated: {result['updated']}")
print(f"Failed: {result['failed']}")

print("\n=== AFTER UPDATE ===")
portfolio.report()

portfolio.risk_check()
