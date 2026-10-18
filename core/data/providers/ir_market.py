import pandas as pd
import pytse_client as tse

from .base import MarketDataProvider


class IranMarketProvider(MarketDataProvider):
    # pytse-client exposes TSETMC price values in rial-denominated native units.
    currency = "IRR"

    def get_price(self, ticker: str) -> float:
        try:
            stock = tse.Ticker(ticker)
        except ValueError:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return stock.last_price
    
    def get_price_history(self, ticker: str, years: int = 1) -> pd.Series:
        try:
            stock = tse.Ticker(ticker)
        except ValueError:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return stock.history.tail(252 * years).set_index('date')['close']
