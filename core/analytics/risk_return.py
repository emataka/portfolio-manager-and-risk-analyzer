import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def _require_observations(values, minimum, name):
    if values is None or len(values) < minimum:
        raise ValueError(f"{name} must contain at least {minimum} observations.")
    if not np.isfinite(np.asarray(values, dtype=float)).all():
        raise ValueError(f"{name} must contain only finite numeric values.")


def calculate_returns(price_history):
    _require_observations(price_history, 2, "Price history")
    if (price_history <= 0).any():
        raise ValueError("Prices must be greater than zero.")
    # Explicitly disable pandas' implicit forward fill across missing prices.
    returns = price_history.pct_change(fill_method=None).dropna()
    if returns.empty:
        raise ValueError("Price history does not contain consecutive valid prices.")
    return returns

def calculate_expected_return(returns):
    _require_observations(returns, 1, "Returns")
    return returns.mean() * TRADING_DAYS_PER_YEAR

def calculate_volatility(returns):
    _require_observations(returns, 2, "Returns")
    return returns.std() * (TRADING_DAYS_PER_YEAR ** 0.5)

def calculate_covariance_matrix(returns_by_ticker):
    df = pd.DataFrame(returns_by_ticker)
    df = df.dropna(how="any")
    _require_observations(df, 2, "Aligned returns")
    return df.cov() * TRADING_DAYS_PER_YEAR

def calculate_portfolio_return(weights, expected_returns):
    missing = set(weights) - set(expected_returns)
    if missing:
        raise ValueError(f"Expected returns are missing tickers: {sorted(missing)}")
    total = 0
    for ticker in weights:
        total += weights[ticker] * expected_returns[ticker]
    return total

def calculate_portfolio_variance(weights, covariance_matrix):
    tickers = list(covariance_matrix.columns)
    missing = set(tickers) - set(weights)
    if missing:
        raise ValueError(f"Weights are missing tickers: {sorted(missing)}")
    weights_array = np.array([weights[ticker] for ticker in tickers])
    covariance_values = covariance_matrix.loc[tickers, tickers].to_numpy(dtype=float)
    if not np.isfinite(covariance_values).all() or not np.isfinite(weights_array).all():
        raise ValueError("Weights and covariance values must be finite.")
    variance = weights_array @ covariance_values @ weights_array
    return max(float(variance), 0.0)
