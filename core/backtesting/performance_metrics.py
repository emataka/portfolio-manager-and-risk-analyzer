TRADING_DAYS_PER_YEAR = 252

def calculate_total_return(portfolio_value):
    return (portfolio_value.iloc[-1] / portfolio_value.iloc[0]) - 1

def calculate_annualized_return(portfolio_value):
    total_return = calculate_total_return(portfolio_value)
    years = len(portfolio_value) / TRADING_DAYS_PER_YEAR
    return (1 + total_return) ** (1 / years) - 1

def calculate_annualized_volatility(portfolio_value):
    daily_returns = portfolio_value.pct_change().dropna()
    return daily_returns.std() * (TRADING_DAYS_PER_YEAR ** 0.5)

def calculate_sharpe_ratio(portfolio_value, risk_free_rate):
    annualized_return = calculate_annualized_return(portfolio_value)
    annualized_volatility = calculate_annualized_volatility(portfolio_value)
    return (annualized_return - risk_free_rate) / annualized_volatility

def calculate_max_drawdown(portfolio_value):
    running_max = portfolio_value.cummax()
    drawdown = (portfolio_value - running_max) / running_max
    return drawdown.min()
