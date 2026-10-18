import pandas as pd
import pytest

from core.backtesting.backtest_engine import (
    run_buy_and_hold_backtest,
    run_rebalancing_backtest,
)
from core.backtesting.performance_metrics import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_total_return,
)


class EqualWeightCapture:
    def __init__(self):
        self.expected_returns = None

    def optimize(self, expected_returns, covariance_matrix):
        self.expected_returns = expected_returns
        tickers = list(covariance_matrix.columns)
        return {ticker: 1 / len(tickers) for ticker in tickers}


class ChangingWeightCapture:
    def __init__(self):
        self.call_count = 0

    def optimize(self, expected_returns, covariance_matrix):
        self.call_count += 1
        if self.call_count == 1:
            return {"A": 0.5, "B": 0.5}
        return {"A": 0.0, "B": 1.0}


def test_rebalance_signal_uses_only_prices_before_execution_day():
    prices = pd.DataFrame(
        {"A": [100.0, 110.0, 121.0, 150.0, 160.0], "B": [100.0, 100.0, 100.0, 100.0, 100.0]},
        index=pd.date_range("2025-01-01", periods=5),
    )
    strategy = EqualWeightCapture()

    result = run_rebalancing_backtest(
        strategy,
        prices,
        initial_capital=1000,
        rebalance_frequency_days=2,
        lookback_days=3,
        transaction_cost_rate=0,
    )

    assert strategy.expected_returns["A"] == pytest.approx(0.10 * 252)
    assert result.index[0] == prices.index[2]
    assert result.iloc[0] == pytest.approx(1000)


def test_rebalance_cost_uses_drifted_weights_and_is_reflected_on_execution_date():
    prices = pd.DataFrame(
        {
            "A": [100.0, 100.0, 100.0, 100.0, 200.0, 200.0, 200.0],
            "B": [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 110.0],
        },
        index=pd.date_range("2025-01-01", periods=7),
    )

    result = run_rebalancing_backtest(
        ChangingWeightCapture(),
        prices,
        initial_capital=1000,
        rebalance_frequency_days=2,
        lookback_days=3,
        transaction_cost_rate=0.01,
    )

    # First entry costs 10. By the next rebalance, A/B drifted to 2/3 and 1/3.
    # Moving to 0/1 target weights has 4/3 turnover, costing 19.8 on 1,485.
    assert result.loc[prices.index[3]] == pytest.approx(990)
    assert result.loc[prices.index[4]] == pytest.approx(1485)
    assert result.loc[prices.index[5]] == pytest.approx(1465.2)
    assert result.loc[prices.index[6]] == pytest.approx(1611.72)


def test_rebalancing_rejects_insufficient_history():
    prices = pd.DataFrame({"A": [100.0, 101.0, 102.0]})

    with pytest.raises(ValueError, match="Not enough price history"):
        run_rebalancing_backtest(EqualWeightCapture(), prices, lookback_days=3)


def test_buy_and_hold_validates_weight_sum():
    prices = pd.DataFrame({"A": [100.0, 101.0], "B": [100.0, 99.0]})

    with pytest.raises(ValueError, match="sum to one"):
        run_buy_and_hold_backtest({"A": 0.2, "B": 0.2}, prices)


def test_max_drawdown_and_return_metrics_have_hand_computable_values():
    values = pd.Series([100.0, 110.0, 99.0, 121.0])

    assert calculate_total_return(values) == pytest.approx(0.21)
    assert calculate_max_drawdown(values) == pytest.approx(-0.10)
    assert calculate_annualized_return(values) > 0
    assert calculate_annualized_volatility(values) > 0
    assert calculate_sharpe_ratio(values, risk_free_rate=0) > 0


def test_sharpe_is_rejected_for_zero_volatility():
    with pytest.raises(ValueError, match="zero"):
        calculate_sharpe_ratio(pd.Series([100.0, 100.0, 100.0]), risk_free_rate=0)
