from abc import ABC, abstractmethod


class OptimizationStrategy(ABC):
    @abstractmethod
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        """Return optimal weights as a dict {ticker: weight}, summing to 1."""
        ...
