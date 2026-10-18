import numpy as np


def calculate_risky_allocation(portfolio_return, portfolio_variance, risk_aversion_coefficient, risk_free_rate):
    return calculate_risky_allocation_details(
        portfolio_return,
        portfolio_variance,
        risk_aversion_coefficient,
        risk_free_rate,
    )["risky_allocation"]


def calculate_risky_allocation_details(
    portfolio_return,
    portfolio_variance,
    risk_aversion_coefficient,
    risk_free_rate,
):
    values = [portfolio_return, portfolio_variance, risk_aversion_coefficient, risk_free_rate]
    if not np.isfinite(values).all():
        raise ValueError("Allocation inputs must be finite.")
    if portfolio_variance <= 0:
        raise ValueError("portfolio_variance must be greater than zero.")
    if risk_aversion_coefficient <= 0:
        raise ValueError("risk_aversion_coefficient must be greater than zero.")
    raw_allocation = (portfolio_return - risk_free_rate) / (
        risk_aversion_coefficient * portfolio_variance
    )
    return {
        "raw_risky_allocation": raw_allocation,
        "risky_allocation": max(0, min(raw_allocation, 1)),
    }
