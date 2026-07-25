import yfinance as yf
from models.portfolio import Portfolio

class MarketDataService:
    def get_price(self, ticker: str) -> float:
        ticker = ticker.upper()
        
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        
        if history.empty:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return history["Close"].iloc[0]
    
    def update_portfolio_prices(self, portfolio: Portfolio) -> dict:
        updated = 0
        failed = 0
        
        for asset in portfolio.assets:
            try:
                new_price = self.get_price(asset.ticker)
                asset.update_price(new_price)
                updated += 1
            except ValueError as e:
                print(f"Failed to update {asset.ticker}: {e}")
                failed += 1
        
        return {
            "updated": updated,
            "failed": failed
        }