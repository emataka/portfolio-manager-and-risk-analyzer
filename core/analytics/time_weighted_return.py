from dataclasses import dataclass
from datetime import datetime
import math
import numbers


@dataclass(frozen=True)
class ValuationPoint:
    """Portfolio value immediately before an external flow at a timestamp.

    ``external_flow_after`` is positive for capital entering the portfolio and
    negative for capital leaving it. Internal income, fees, and trades are not
    external flows; their effects belong in the portfolio valuation.
    """

    timestamp: datetime
    market_value: float
    currency: str
    external_flow_after: float = 0.0


def calculate_time_weighted_return(points):
    """Geometrically link sub-period returns around external cash flows.

    Each observation is a valuation immediately before any external flow at
    that timestamp. The flow is then applied to form the next sub-period's
    beginning value. The last observation must have no flow after it.

    The result is a decimal return for the interval, not an annualized rate.
    Callers must supply reliable valuations at the start, end, and around every
    external flow. This function does not retrieve or infer historical prices.
    """
    if not isinstance(points, (list, tuple)) or len(points) < 2:
        raise ValueError("At least two valuation points are required.")

    validated = [_validate_point(point, index) for index, point in enumerate(points)]
    currency = validated[0].currency
    if any(point.currency != currency for point in validated):
        raise ValueError("All valuation points must use the same currency.")

    for previous, current in zip(validated, validated[1:]):
        if current.timestamp <= previous.timestamp:
            raise ValueError("Valuation timestamps must be strictly increasing.")

    if validated[-1].external_flow_after != 0:
        raise ValueError("The final valuation point cannot have a flow after it.")

    growth_factor = 1.0
    for previous, current in zip(validated, validated[1:]):
        beginning_value = previous.market_value + previous.external_flow_after
        if beginning_value <= 0:
            raise ValueError("Beginning value after external flow must be greater than zero.")
        subperiod_growth = current.market_value / beginning_value
        if not math.isfinite(subperiod_growth):
            raise ValueError("Sub-period return calculation exceeded the finite numeric range.")
        growth_factor *= subperiod_growth
        if not math.isfinite(growth_factor):
            raise ValueError("Linked return calculation exceeded the finite numeric range.")

    return growth_factor - 1.0


def _validate_point(point, index):
    if not isinstance(point, ValuationPoint):
        raise TypeError(f"Valuation point at position {index} must be a ValuationPoint.")
    if (
        not isinstance(point.timestamp, datetime)
        or point.timestamp.tzinfo is None
        or point.timestamp.utcoffset() is None
    ):
        raise ValueError(f"Valuation point at position {index} needs a timezone-aware timestamp.")
    if isinstance(point.market_value, bool) or not isinstance(point.market_value, numbers.Real):
        raise ValueError(f"Market value at position {index} must be numeric.")
    if not math.isfinite(point.market_value) or point.market_value < 0:
        raise ValueError(f"Market value at position {index} must be finite and non-negative.")
    if isinstance(point.external_flow_after, bool) or not isinstance(
        point.external_flow_after, numbers.Real
    ):
        raise ValueError(f"External flow at position {index} must be numeric.")
    if not math.isfinite(point.external_flow_after):
        raise ValueError(f"External flow at position {index} must be finite.")
    if point.currency not in {"USD", "IRR"}:
        raise ValueError(f"Currency at position {index} must be USD or IRR.")
    return point


def validate_valuation_point(point):
    """Validate one valuation observation for persistence or calculation."""
    return _validate_point(point, 0)
