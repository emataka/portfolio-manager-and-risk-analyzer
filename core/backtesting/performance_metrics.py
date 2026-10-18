import numpy as np

TRADING_DAYS_PER_YEAR = 252


def _validated_portfolio_value(portfolio_value, minimum=1):
    if portfolio_value is None or len(portfolio_value) < minimum:
        raise ValueError(f"Portfolio value must contain at least {minimum} observations.")
    values = np.asarray(portfolio_value, dtype=float)
    if not np.isfinite(values).all() or (values <= 0).any():
        raise ValueError("Portfolio values must be finite and greater than zero.")
    return values


def calculate_total_return(portfolio_value):
    values = _validated_portfolio_value(portfolio_value, minimum=2)
    return (values[-1] / values[0]) - 1

def calculate_annualized_return(portfolio_value):
    values = _validated_portfolio_value(portfolio_value, minimum=2)
    total_return = calculate_total_return(portfolio_value)
    years = (len(values) - 1) / TRADING_DAYS_PER_YEAR
    return (1 + total_return) ** (1 / years) - 1

def calculate_annualized_volatility(portfolio_value):
    values = _validated_portfolio_value(portfolio_value, minimum=2)
    daily_returns = np.diff(values) / values[:-1]
    return daily_returns.std(ddof=1) * (TRADING_DAYS_PER_YEAR ** 0.5)

def calculate_sharpe_ratio(portfolio_value, risk_free_rate):
    if not np.isfinite(risk_free_rate) or risk_free_rate <= -1:
        raise ValueError("risk_free_rate must be finite and greater than -100%.")
    values = _validated_portfolio_value(portfolio_value, minimum=2)
    daily_returns = np.diff(values) / values[:-1]
    daily_risk_free_rate = (1 + risk_free_rate) ** (1 / TRADING_DAYS_PER_YEAR) - 1
    excess_returns = daily_returns - daily_risk_free_rate
    daily_volatility = daily_returns.std(ddof=1)
    if daily_volatility == 0:
        raise ValueError("Sharpe ratio is undefined when portfolio volatility is zero.")
    return (excess_returns.mean() / daily_volatility) * (TRADING_DAYS_PER_YEAR ** 0.5)

def calculate_max_drawdown(portfolio_value):
    values = _validated_portfolio_value(portfolio_value)
    running_max = np.maximum.accumulate(values)
    drawdown = (values - running_max) / running_max
    return float(drawdown.min())
