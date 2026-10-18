from dataclasses import dataclass
from datetime import datetime, timezone
import math
import numbers

from .asset import Asset


@dataclass(frozen=True)
class Transaction:
    ticker: str
    market: str
    side: str
    quantity: float
    price: float
    fees: float
    currency: str
    executed_at: datetime

    def __init__(
        self,
        ticker,
        market,
        side,
        quantity,
        price,
        fees=0,
        currency=None,
        executed_at=None,
    ):
        if not isinstance(ticker, str) or not ticker.strip():
            raise ValueError("Transaction ticker must be a non-empty string.")
        ticker = ticker.strip().upper()
        if not isinstance(market, str):
            raise ValueError("Transaction market must be a string.")
        market = market.upper()
        if market not in Asset.MARKET_CURRENCIES:
            raise ValueError(f"Unsupported transaction market: {market!r}.")

        if not isinstance(side, str):
            raise ValueError("Transaction side must be a string.")
        side = side.upper()
        if side not in {"OPENING_BALANCE", "BUY", "SELL"}:
            raise ValueError("Transaction side must be OPENING_BALANCE, BUY, or SELL.")

        expected_currency = Asset.MARKET_CURRENCIES[market]
        currency = expected_currency if currency is None else currency
        currency = currency.upper() if isinstance(currency, str) else currency
        if currency != expected_currency:
            raise ValueError(
                f"Market {market} transactions must use {expected_currency}."
            )

        _set_frozen(self, "ticker", ticker)
        _set_frozen(self, "market", market)
        _set_frozen(self, "side", side)
        _set_frozen(self, "quantity", _number(quantity, "quantity", minimum=0, strict=True))
        _set_frozen(self, "price", _number(price, "price", minimum=0, strict=True))
        _set_frozen(self, "fees", _number(fees, "fees", minimum=0, strict=False))
        _set_frozen(self, "currency", currency)

        if executed_at is None:
            executed_at = datetime.now(timezone.utc)
        elif isinstance(executed_at, str):
            try:
                executed_at = datetime.fromisoformat(executed_at)
            except ValueError as error:
                raise ValueError("executed_at must be a valid ISO 8601 timestamp.") from error
        if (
            not isinstance(executed_at, datetime)
            or executed_at.tzinfo is None
            or executed_at.utcoffset() is None
        ):
            raise ValueError("executed_at must be a timezone-aware datetime.")
        _set_frozen(self, "executed_at", executed_at.astimezone(timezone.utc))

    def to_record(self):
        return {
            "ticker": self.ticker,
            "market": self.market,
            "side": self.side,
            "quantity": self.quantity,
            "price": self.price,
            "fees": self.fees,
            "currency": self.currency,
            "executed_at": self.executed_at.isoformat(),
        }


def _set_frozen(instance, name, value):
    object.__setattr__(instance, name, value)


def _number(value, field, *, minimum, strict):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"Transaction {field} must be numeric.")
    value = float(value)
    if not math.isfinite(value) or (value <= minimum if strict else value < minimum):
        comparison = "greater than" if strict else "at least"
        raise ValueError(f"Transaction {field} must be finite and {comparison} {minimum}.")
    return value
