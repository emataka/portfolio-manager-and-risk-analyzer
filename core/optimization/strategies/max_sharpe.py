import numpy as np
from scipy.optimize import minimize

from .base import OptimizationStrategy


class MaxSharpeStrategy(OptimizationStrategy):
    def __init__(self, risk_free_rate=0.0):
        self.risk_free_rate = risk_free_rate
    
    def optimize(self, expected_returns, covariance_matrix) -> dict:
        tickers = list(covariance_matrix.columns)
        n = len(tickers)
        cov = covariance_matrix.values
        returns = np.array([expected_returns[ticker] for ticker in tickers])
        
        def negative_sharpe_ratio(weights):
            portfolio_return = weights @ returns
            portfolio_volatility = np.sqrt(weights @ cov @ weights)
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
        
        return {ticker: weight for ticker, weight in zip(tickers, result.x)}
