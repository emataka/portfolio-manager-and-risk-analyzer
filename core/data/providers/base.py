from abc import ABC, abstractmethod


class MarketDataProvider(ABC):
    @abstractmethod
    def get_price(self, ticker: str) -> float:
        """Return the current price for a given ticker."""
        ...