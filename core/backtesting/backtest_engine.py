import numpy as np
import pandas as pd

from core.analytics.risk_return import (
    calculate_covariance_matrix,
    calculate_expected_return,
    calculate_returns,
)


def run_buy_and_hold_backtest(weights, price_histories, initial_capital=10000):
    price_df = _validated_prices(price_histories)
    _validate_capital(initial_capital)
    _validate_weights(weights, list(price_df.columns))

    shares = {}
    for ticker, weight in weights.items():
        dollars_allocated = initial_capital * weight
        initial_price = price_df[ticker].iloc[0]
        shares[ticker] = dollars_allocated / initial_price

    portfolio_value = pd.Series(0.0, index=price_df.index)
    for ticker, share_count in shares.items():
        portfolio_value += share_count * price_df[ticker]

    return portfolio_value


def run_rebalancing_backtest(
    optimization_strategy,
    price_histories,
    initial_capital=10000,
    rebalance_frequency_days=63,
    lookback_days=252,
    transaction_cost_rate=0.001,
):
    price_df = _validated_prices(price_histories)
    _validate_capital(initial_capital)
    if not isinstance(lookback_days, int) or lookback_days < 3:
        raise ValueError("lookback_days must be an integer of at least 3.")
    if not isinstance(rebalance_frequency_days, int) or rebalance_frequency_days < 1:
        raise ValueError("rebalance_frequency_days must be a positive integer.")
    if not np.isfinite(transaction_cost_rate) or not 0 <= transaction_cost_rate < 1:
        raise ValueError("transaction_cost_rate must be finite and between zero and one.")

    tickers = list(price_df.columns)
    # Use only observations before each rebalance date when estimating parameters.
    rebalance_positions = list(range(lookback_days, len(price_df), rebalance_frequency_days))
    if not rebalance_positions:
        raise ValueError("Not enough price history for the requested lookback period.")

    current_shares = {ticker: 0 for ticker in tickers}
    first_observation = price_df.index[rebalance_positions[0] - 1]
    value_pieces = [pd.Series([initial_capital], index=[first_observation])]

    for i, rebalance_position in enumerate(rebalance_positions):
        lookback_window = price_df.iloc[rebalance_position - lookback_days:rebalance_position]
        returns_by_ticker = {t: calculate_returns(lookback_window[t]) for t in tickers}
        expected_returns = {
            t: calculate_expected_return(returns) for t, returns in returns_by_ticker.items()
        }
        covariance_matrix = calculate_covariance_matrix(returns_by_ticker)
        new_weights = optimization_strategy.optimize(expected_returns, covariance_matrix)
        _validate_weights(new_weights, tickers)

        rebalance_date = price_df.index[rebalance_position]
        current_prices = price_df.iloc[rebalance_position]
        portfolio_value = sum(current_shares[t] * current_prices[t] for t in tickers)
        if portfolio_value == 0:
            portfolio_value = initial_capital
            pre_trade_weights = {ticker: 0.0 for ticker in tickers}
        else:
            pre_trade_weights = {
                ticker: current_shares[ticker] * current_prices[ticker] / portfolio_value
                for ticker in tickers
            }

        # Drifted weights, not the previous targets, determine the trades needed.
        turnover = sum(abs(new_weights[t] - pre_trade_weights[t]) for t in tickers)
        transaction_cost = turnover * portfolio_value * transaction_cost_rate
        portfolio_value_after_cost = portfolio_value - transaction_cost

        for ticker in tickers:
            dollars = portfolio_value_after_cost * new_weights[ticker]
            current_shares[ticker] = dollars / current_prices[ticker]

        if i + 1 < len(rebalance_positions):
            next_rebalance_position = rebalance_positions[i + 1]
            period_prices = price_df.iloc[rebalance_position:next_rebalance_position]
        else:
            period_prices = price_df.iloc[rebalance_position:]

        period_value = pd.Series(0.0, index=period_prices.index)
        for ticker in tickers:
            period_value += current_shares[ticker] * period_prices[ticker]
        value_pieces.append(period_value)

    full_value_series = pd.concat(value_pieces)
    return full_value_series[~full_value_series.index.duplicated(keep="last")]


def run_allocated_backtest(
    optimization_strategy,
    price_histories,
    risky_allocation,
    risk_free_rate,
    initial_capital=10000,
    rebalance_frequency_days=63,
    lookback_days=252,
    transaction_cost_rate=0.001,
):
    if not np.isfinite(risky_allocation) or not 0 <= risky_allocation <= 1:
        raise ValueError("risky_allocation must be between 0 and 1.")
    if not np.isfinite(risk_free_rate) or risk_free_rate <= -1:
        raise ValueError("risk_free_rate must be finite and greater than -100%.")
    _validate_capital(initial_capital)

    risky_capital = initial_capital * risky_allocation
    risk_free_capital = initial_capital * (1 - risky_allocation)

    if risky_allocation == 0:
        price_df = _validated_prices(price_histories)
        if not isinstance(lookback_days, int) or lookback_days < 3:
            raise ValueError("lookback_days must be an integer of at least 3.")
        if len(price_df) <= lookback_days:
            raise ValueError("Not enough price history for the requested lookback period.")
        index = price_df.index[lookback_days - 1:]
        daily_rate = (1 + risk_free_rate) ** (1 / 252) - 1
        return pd.Series(
            [risk_free_capital * (1 + daily_rate) ** day for day in range(len(index))],
            index=index,
        )

    risky_value = run_rebalancing_backtest(
        optimization_strategy,
        price_histories,
        initial_capital=risky_capital,
        rebalance_frequency_days=rebalance_frequency_days,
        lookback_days=lookback_days,
        transaction_cost_rate=transaction_cost_rate,
    )

    daily_rate = (1 + risk_free_rate) ** (1 / 252) - 1
    risk_free_value = pd.Series(
        [risk_free_capital * (1 + daily_rate) ** day for day in range(len(risky_value))],
        index=risky_value.index,
    )
    return risky_value + risk_free_value


def _validated_prices(price_histories):
    price_df = pd.DataFrame(price_histories)
    if price_df.empty or price_df.shape[1] == 0:
        raise ValueError("Price histories must contain at least one ticker and one observation.")
    price_df = price_df.dropna(how="any")
    if price_df.empty:
        raise ValueError("Price histories do not contain aligned observations.")
    if not price_df.index.is_unique:
        raise ValueError("Price histories must have unique observation dates.")
    price_df = price_df.sort_index()
    values = price_df.to_numpy(dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Aligned prices must be finite and greater than zero.")
    return price_df


def _validate_capital(initial_capital):
    if not np.isfinite(initial_capital) or initial_capital <= 0:
        raise ValueError("initial_capital must be finite and greater than zero.")


def _validate_weights(weights, tickers):
    if not isinstance(weights, dict) or set(weights) != set(tickers):
        raise ValueError("Portfolio weights must contain exactly the price-history tickers.")
    values = np.asarray(list(weights.values()), dtype=float)
    if not np.isfinite(values).all() or (values < 0).any() or (values > 1).any():
        raise ValueError("Portfolio weights must be finite and between zero and one.")
    if not np.isclose(values.sum(), 1.0, atol=1e-6):
        raise ValueError("Portfolio weights must sum to one.")
