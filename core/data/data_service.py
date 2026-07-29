from .providers.us_market import USMarketProvider


class MarketDataService:
    def __init__(self):
        self.us_provider = USMarketProvider()
    
    def get_price(self, ticker: str) -> float:
        return self.us_provider.get_price(ticker)
    
    def update_portfolio_prices(self, portfolio) -> dict:
        updated = 0
        failed = 0
        failures = []
        
        for asset in portfolio.assets:
            try:
                new_price = self.get_price(asset.ticker)
                asset.update_price(new_price)
                updated += 1
            except Exception as e:
                failed += 1
                error = {
                    "ticker": asset.ticker,
                    "error": str(e),
                }
                failures.append(error)
        
        return {
            "updated": updated,
            "failed": failed,
            "failures": failures,
        }