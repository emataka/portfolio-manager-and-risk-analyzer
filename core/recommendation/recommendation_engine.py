import pandas as pd

from core.analytics.risk_return import (
    calculate_covariance_matrix,
    calculate_expected_return,
    calculate_portfolio_return,
    calculate_portfolio_variance,
    calculate_returns,
)
from core.recommendation.capital_allocation import calculate_risky_allocation_details


class RecommendationEngine:
    def __init__(self, market_data_service, optimization_strategy, risk_free_rate):
        self.market_data_service = market_data_service
        self.optimization_strategy = optimization_strategy
        self.risk_free_rate = risk_free_rate
    
    def generate_recommendation(self, tickers, market, risk_aversion_coefficient):
        returns_by_ticker = {}
        for ticker in tickers:
            price_history = self.market_data_service.get_price_history(ticker, market)
            returns = calculate_returns(price_history)
            returns_by_ticker[ticker] = returns

        aligned_returns = pd.DataFrame(returns_by_ticker).dropna(how="any")
        if len(aligned_returns) < 2:
            raise ValueError("Not enough common price observations to analyze this portfolio.")
        returns_by_ticker = {
            ticker: aligned_returns[ticker] for ticker in aligned_returns.columns
        }
        
        expected_returns = {
            ticker: calculate_expected_return(returns)
            for ticker, returns in returns_by_ticker.items()
        }
        
        covariance_matrix = calculate_covariance_matrix(returns_by_ticker)
        weights = self.optimization_strategy.optimize(expected_returns, covariance_matrix)
        portfolio_return = calculate_portfolio_return(weights, expected_returns)
        portfolio_variance = calculate_portfolio_variance(weights, covariance_matrix)
        allocation = calculate_risky_allocation_details(
            portfolio_return, portfolio_variance, risk_aversion_coefficient, self.risk_free_rate
        )
        
        return {
            "portfolio_return": portfolio_return,
            "weights": weights,
            "risky_allocation": allocation["risky_allocation"],
            "raw_risky_allocation": allocation["raw_risky_allocation"],
            "portfolio_variance": portfolio_variance,
            "observation_count": len(aligned_returns),
            "history_start": aligned_returns.index[0],
            "history_end": aligned_returns.index[-1],
        }
