from dataclasses import dataclass
from datetime import datetime, timezone
import math
import numbers


@dataclass(frozen=True)
class CashTransaction:
    side: str
    amount: float
    currency: str
    executed_at: datetime

    def __init__(self, side, amount, currency, executed_at=None):
        if not isinstance(side, str):
            raise ValueError("Cash transaction side must be a string.")
        side = side.upper()
        if side not in {
            "OPENING_CASH", "CASH_DEPOSIT", "CASH_WITHDRAWAL", "CASH_RECONCILIATION"
        }:
            raise ValueError("Unsupported cash transaction side.")
        if not isinstance(currency, str) or currency.upper() not in {"USD", "IRR"}:
            raise ValueError("Cash currency must be USD or IRR.")
        if isinstance(amount, bool) or not isinstance(amount, numbers.Real):
            raise ValueError("Cash transaction amount must be numeric.")
        amount = float(amount)
        if not math.isfinite(amount):
            raise ValueError("Cash transaction amount must be finite.")
        if side != "CASH_RECONCILIATION" and amount <= 0:
            raise ValueError("Cash transaction amount must be greater than zero.")

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

        object.__setattr__(self, "side", side)
        object.__setattr__(self, "amount", amount)
        object.__setattr__(self, "currency", currency.upper())
        object.__setattr__(self, "executed_at", executed_at.astimezone(timezone.utc))

    def to_record(self):
        return {
            "type": "cash",
            "side": self.side,
            "amount": self.amount,
            "currency": self.currency,
            "executed_at": self.executed_at.isoformat(),
        }
