import numpy as np
from scipy.optimize import minimize

from .base import OptimizationStrategy


class MinVarianceStrategy(OptimizationStrategy):
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        tickers = list(covariance_matrix.columns)
        n = len(tickers)
        cov = covariance_matrix.values
        
        def portfolio_variance(weights):
            return weights @ cov @ weights
        
        constraints = [
            {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}
        ]
        bounds = [(0, 1) for _ in range(n)]
        initial_guess = np.array([1 / n] * n)
        
        result = minimize(
            portfolio_variance,
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        
        return {ticker: weight for ticker, weight in zip(tickers, result.x)}
