import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252

def calculate_returns(price_history):
    return price_history.pct_change().dropna()

def calculate_expected_return(returns):
    return returns.mean() * TRADING_DAYS_PER_YEAR

def calculate_volatility(returns):
    return returns.std() * (TRADING_DAYS_PER_YEAR ** 0.5)

def calculate_covariance_matrix(returns_by_ticker):
    df = pd.DataFrame(returns_by_ticker)
    return df.dropna().cov() * TRADING_DAYS_PER_YEAR

def calculate_portfolio_return(weights, expected_returns):
    total = 0
    for ticker in weights:
        total += weights[ticker] * expected_returns[ticker]
    return total

def calculate_portfolio_variance(weights, covariance_matrix):
    tickers = list(covariance_matrix.columns)
    weights_array = np.array([weights[ticker] for ticker in tickers])
    return weights_array @ covariance_matrix.values @ weights_array
