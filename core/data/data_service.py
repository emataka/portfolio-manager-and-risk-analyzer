from .providers.ir_market import IranMarketProvider
from .providers.us_market import USMarketProvider


class MarketDataService:
    def __init__(self):
        self.us_provider = USMarketProvider()
        self.ir_provider = IranMarketProvider()
    
    def get_price(self, ticker: str, market: str) -> float:
        if market == "US":
            return self.us_provider.get_price(ticker)
        elif market == "IR":
            return self.ir_provider.get_price(ticker)
        else:
            raise ValueError(f"Unknown market: {market}")
    
    def get_price_history(self, ticker: str, market: str):
        if market == "US":
            return self.us_provider.get_price_history(ticker)
        elif market == "IR":
            return self.ir_provider.get_price_history(ticker)
        else:
            raise ValueError(f"Unknown market: {market}")
    
    def update_portfolio_prices(self, portfolio) -> dict:
        updated = 0
        failed = 0
        failures = []
        
        for asset in portfolio.assets:
            try:
                new_price = self.get_price(asset.ticker, asset.market)
                asset.update_price(new_price)
                updated += 1
            except Exception as e:  # noqa: BLE001
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
