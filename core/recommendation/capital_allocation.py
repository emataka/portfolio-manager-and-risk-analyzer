def calculate_risky_allocation(portfolio_return, portfolio_variance, risk_aversion_coefficient, risk_free_rate):
    y = (portfolio_return - risk_free_rate) / (risk_aversion_coefficient * portfolio_variance)
    return max(0, min(y, 1))
