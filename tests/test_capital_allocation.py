import pytest

from core.recommendation.capital_allocation import (
    calculate_risky_allocation,
    calculate_risky_allocation_details,
)


def test_risky_allocation_is_clamped_to_supported_range():
    assert calculate_risky_allocation(0.12, 0.04, 2, 0.02) == pytest.approx(1.0)
    assert calculate_risky_allocation(0.01, 0.04, 2, 0.02) == 0


def test_risky_allocation_rejects_invalid_variance_and_risk_aversion():
    with pytest.raises(ValueError, match="portfolio_variance"):
        calculate_risky_allocation(0.12, 0, 2, 0.02)
    with pytest.raises(ValueError, match="risk_aversion"):
        calculate_risky_allocation(0.12, 0.04, 0, 0.02)


def test_allocation_details_keep_the_unclamped_model_output_visible():
    result = calculate_risky_allocation_details(0.566, 0.128**2, 2.5, 0.05)

    assert result["raw_risky_allocation"] > 1
    assert result["risky_allocation"] == 1
