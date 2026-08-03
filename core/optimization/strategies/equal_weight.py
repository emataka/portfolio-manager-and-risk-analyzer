from .base import OptimizationStrategy


class EqualWeightStrategy(OptimizationStrategy):
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        count = len(expected_returns)
        weight = 1 / count 
        return {ticker: weight for ticker in expected_returns.keys()}  # noqa: SIM118
