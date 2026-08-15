from abc import ABC, abstractmethod


class MarketDataProvider(ABC):
    @abstractmethod
    def get_price(self, ticker: str) -> float:
        """Return the current price for a given ticker."""
        ...

    @abstractmethod
    def get_price_history(self, ticker: str, years: int = 1):
        """Return a pandas Series of daily closing prices, indexed by date, for roughly the past `years` years."""
        ...
