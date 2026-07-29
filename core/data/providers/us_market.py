import yfinance as yf

from .base import MarketDataProvider


class USMarketProvider(MarketDataProvider):
    def get_price(self, ticker: str) -> float:
        ticker = ticker.upper()
        
        stock = yf.Ticker(ticker)
        history = stock.history(period="1d")
        
        if history.empty:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return history["Close"].iloc[0]
