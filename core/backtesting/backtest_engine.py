import pandas as pd

from core.analytics.risk_return import (
    calculate_covariance_matrix,
    calculate_expected_return,
    calculate_returns,
)


def run_buy_and_hold_backtest(weights, price_histories, initial_capital=10000):
    price_df = pd.DataFrame(price_histories).dropna()
    
    shares = {}
    for ticker, weight in weights.items():
        dollars_allocated = initial_capital * weight
        initial_price = price_df[ticker].iloc[0]
        shares[ticker] = dollars_allocated / initial_price
    
    portfolio_value = pd.Series(0.0, index=price_df.index) # ask claude what this line is about, later
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
    price_df = pd.DataFrame(price_histories).dropna()
    tickers = list(price_df.columns)
    
    rebalance_dates = price_df.index[lookback_days::rebalance_frequency_days]
    
    current_shares = {ticker: 0 for ticker in tickers}
    current_weights = {ticker: 0 for ticker in tickers}
    value_pieces = []
    
    for i, rebalance_date in enumerate(rebalance_dates):
        lookback_window = price_df.loc[:rebalance_date].tail(lookback_days)
        returns_by_ticker = {t: calculate_returns(lookback_window[t]) for t in tickers}
        expected_returns = {t: calculate_expected_return(r) for t, r in returns_by_ticker.items()}
        covariance_matrix = calculate_covariance_matrix(returns_by_ticker)
        new_weights = optimization_strategy.optimize(expected_returns, covariance_matrix)
        
        current_prices = price_df.loc[rebalance_date]
        portfolio_value = sum(current_shares[t] * current_prices[t] for t in tickers)
        if portfolio_value == 0:
            portfolio_value = initial_capital
        
        turnover = sum(abs(new_weights[t] - current_weights[t]) for t in tickers)
        transaction_cost = turnover * portfolio_value * transaction_cost_rate
        portfolio_value_after_cost = portfolio_value - transaction_cost
        
        for t in tickers:
            dollars = portfolio_value_after_cost * new_weights[t]
            current_shares[t] = dollars / current_prices[t]
        current_weights = new_weights
        
        if i + 1 < len(rebalance_dates):
            period_prices = price_df.loc[rebalance_date:rebalance_dates[i + 1]]
        else:
            period_prices = price_df.loc[rebalance_date:]
        
        period_value = pd.Series(0.0, index=period_prices.index)
        for t in tickers:
            period_value += current_shares[t] * period_prices[t]
        value_pieces.append(period_value)
    
    full_value_series = pd.concat(value_pieces)
    return full_value_series[~full_value_series.index.duplicated(keep="first")]

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
    risky_capital = initial_capital * risky_allocation
    risk_free_capital = initial_capital * (1 - risky_allocation)
    
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
