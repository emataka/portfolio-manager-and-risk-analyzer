from datetime import datetime, timezone

import pytest

from core.analytics.time_weighted_return import (
    ValuationPoint,
    calculate_time_weighted_return,
)


def point(day, value, flow=0, currency="USD"):
    return ValuationPoint(
        datetime(2025, 1, day, tzinfo=timezone.utc),
        value,
        currency,
        flow,
    )


def test_time_weighted_return_without_external_flows():
    result = calculate_time_weighted_return([point(1, 100), point(2, 120)])

    assert result == pytest.approx(0.20)


def test_deposit_does_not_inflate_investment_return():
    result = calculate_time_weighted_return(
        [point(1, 100), point(2, 110, flow=100), point(3, 231)]
    )

    assert result == pytest.approx(0.21)


def test_withdrawal_does_not_reduce_investment_return():
    result = calculate_time_weighted_return(
        [point(1, 100), point(2, 110, flow=-55), point(3, 60.5)]
    )

    assert result == pytest.approx(0.21)


def test_multiple_external_flows_geometrically_link_independently_calculated_periods():
    result = calculate_time_weighted_return(
        [
            point(1, 100),          # start with 100
            point(2, 110, flow=50),  # +10%, then deposit 50
            point(3, 168, flow=-20),  # +5%, then withdraw 20
            point(4, 162.8),        # +10% on the remaining 148
        ]
    )

    # (110 / 100) * (168 / 160) * (162.8 / 148) - 1 = 27.05%
    assert result == pytest.approx(0.2705)


def test_opening_capital_can_be_represented_as_initial_flow():
    result = calculate_time_weighted_return(
        [point(1, 0, flow=100), point(2, 110)]
    )

    assert result == pytest.approx(0.10)


@pytest.mark.parametrize(
    "points, message",
    [
        ([point(1, 100)], "At least two"),
        ([point(2, 100), point(1, 110)], "strictly increasing"),
        ([point(1, 100, flow=-100), point(2, 10)], "Beginning value"),
        ([point(1, 100), point(2, 110, flow=1)], "final valuation point"),
        ([point(1, 100, currency="USD"), point(2, 110, currency="IRR")], "same currency"),
        ([ValuationPoint(datetime(2025, 1, 1), 100, "USD"), point(2, 110)], "timezone-aware"),
        ([point(1, float("nan")), point(2, 110)], "finite and non-negative"),
        ([point(1, 1e-308), point(2, 1e308)], "finite numeric range"),
    ],
)
def test_time_weighted_return_rejects_invalid_valuation_series(points, message):
    with pytest.raises(ValueError, match=message):
        calculate_time_weighted_return(points)
