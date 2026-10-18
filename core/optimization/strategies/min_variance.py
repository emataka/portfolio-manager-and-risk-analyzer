import numpy as np
from scipy.optimize import minimize

from .base import OptimizationStrategy


class MinVarianceStrategy(OptimizationStrategy):
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        tickers = list(covariance_matrix.columns)
        n = len(tickers)
        cov = covariance_matrix.loc[tickers, tickers].to_numpy(dtype=float)
        if n == 0 or covariance_matrix.shape != (n, n):
            raise ValueError("Covariance matrix must be non-empty and square.")
        if not np.isfinite(cov).all():
            raise ValueError("Covariance values must be finite.")
        
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
        if not result.success or not np.isfinite(result.x).all():
            raise RuntimeError(f"Minimum-variance optimization failed: {result.message}")
        weights = np.clip(result.x, 0.0, 1.0)
        weight_sum = weights.sum()
        if weight_sum <= 0:
            raise RuntimeError("Minimum-variance optimization returned no usable weights.")
        weights /= weight_sum
        return {ticker: weight for ticker, weight in zip(tickers, weights)}
