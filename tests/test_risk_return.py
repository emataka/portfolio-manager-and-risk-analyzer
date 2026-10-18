import numpy as np
import pandas as pd
import pytest

from core.analytics.risk_return import (
    calculate_covariance_matrix,
    calculate_expected_return,
    calculate_portfolio_variance,
    calculate_returns,
    calculate_volatility,
)


def test_calculate_returns_does_not_forward_fill_missing_prices():
    prices = pd.Series([100.0, np.nan, 110.0])

    with pytest.raises(ValueError, match="finite"):
        calculate_returns(prices)


def test_annualized_return_and_volatility_use_daily_observations():
    returns = pd.Series([0.01, -0.01, 0.02])

    assert calculate_expected_return(returns) == pytest.approx(0.02 * 252 / 3)
    assert calculate_volatility(returns) == pytest.approx(returns.std() * np.sqrt(252))


def test_covariance_uses_aligned_observations():
    returns = {
        "A": pd.Series([0.01, 0.02, 0.03], index=[1, 2, 3]),
        "B": pd.Series([0.02, 0.04], index=[2, 3]),
    }

    covariance = calculate_covariance_matrix(returns)

    expected = pd.DataFrame({"A": [0.02, 0.03], "B": [0.02, 0.04]}).cov() * 252
    pd.testing.assert_frame_equal(covariance, expected)


def test_portfolio_variance_rejects_missing_weights():
    covariance = pd.DataFrame([[0.04, 0.0], [0.0, 0.09]], columns=["A", "B"], index=["A", "B"])

    with pytest.raises(ValueError, match="missing tickers"):
        calculate_portfolio_variance({"A": 1.0}, covariance)
