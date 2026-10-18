import numpy as np
from scipy.optimize import minimize

from .base import OptimizationStrategy


class MaxSharpeStrategy(OptimizationStrategy):
    def __init__(self, risk_free_rate=0.0):
        self.risk_free_rate = risk_free_rate
    
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        tickers = list(covariance_matrix.columns)
        n = len(tickers)
        cov = covariance_matrix.loc[tickers, tickers].to_numpy(dtype=float)
        if n == 0 or covariance_matrix.shape != (n, n):
            raise ValueError("Covariance matrix must be non-empty and square.")
        if any(ticker not in expected_returns for ticker in tickers):
            raise ValueError("Expected returns must contain every covariance-matrix ticker.")
        returns = np.asarray([expected_returns[ticker] for ticker in tickers], dtype=float)
        if not np.isfinite(returns).all() or not np.isfinite(cov).all():
            raise ValueError("Expected returns and covariance values must be finite.")
        if not np.isfinite(self.risk_free_rate):
            raise ValueError("risk_free_rate must be finite.")
        
        def negative_sharpe_ratio(weights):
            portfolio_return = weights @ returns
            portfolio_volatility = np.sqrt(weights @ cov @ weights)
            if portfolio_volatility <= 0:
                return 1e12
            sharpe_ratio = (portfolio_return - self.risk_free_rate) / portfolio_volatility
            return -sharpe_ratio
        
        constraints = [
            {"type": "eq", "fun": lambda weights: np.sum(weights) - 1}
        ]
        bounds = [(0, 1) for _ in range(n)]
        initial_guess = np.array([1 / n] * n)
        
        result = minimize(
            negative_sharpe_ratio,
            initial_guess,
            method="SLSQP",
            bounds=bounds,
            constraints=constraints
        )
        if not result.success or not np.isfinite(result.x).all():
            raise RuntimeError(f"Maximum-Sharpe optimization failed: {result.message}")
        weights = np.clip(result.x, 0.0, 1.0)
        weight_sum = weights.sum()
        if weight_sum <= 0:
            raise RuntimeError("Maximum-Sharpe optimization returned no usable weights.")
        weights /= weight_sum
        return {ticker: weight for ticker, weight in zip(tickers, weights)}
