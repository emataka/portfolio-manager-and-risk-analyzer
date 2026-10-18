import inspect

import pandas as pd
import yfinance as yf

from .base import MarketDataProvider


class USMarketProvider(MarketDataProvider):
    currency = "USD"

    def get_price(self, ticker: str) -> float:
        ticker = ticker.upper()
        
        stock = yf.Ticker(ticker)
        # Live portfolio valuation needs the tradable, unadjusted quote.
        history = _history(stock, period="1d", auto_adjust=False)
        
        if history.empty:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return history["Close"].iloc[0]

    def get_price_history(self, ticker: str, years: int = 1) -> pd.Series:
        ticker = ticker.upper()
        
        stock = yf.Ticker(ticker)
        # Historical backtests use adjusted prices to account for splits/dividends.
        history = _history(stock, period=f"{years}y", auto_adjust=True)
        
        if history.empty:
            raise ValueError(f"Ticker '{ticker}' not found.")
        
        return history["Close"]


def _history(stock, *, period, auto_adjust):
    """Request explicit adjustment semantics while supporting simple wrappers."""
    history_method = stock.history
    parameters = inspect.signature(history_method).parameters
    supports_auto_adjust = "auto_adjust" in parameters or any(
        parameter.kind == inspect.Parameter.VAR_KEYWORD
        for parameter in parameters.values()
    )
    kwargs = {"period": period}
    if supports_auto_adjust:
        kwargs["auto_adjust"] = auto_adjust
    return history_method(**kwargs)
