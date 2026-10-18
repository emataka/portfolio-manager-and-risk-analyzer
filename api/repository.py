import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy import select

from core.models.cash_transaction import CashTransaction
from core.models.portfolio import Portfolio
from core.persistence.portfolio_store import replay_transactions

from api.database import make_session_factory
from api.models import (
    PortfolioEventRow,
    PortfolioPriceRow,
    PortfolioRow,
    PortfolioValuationRow,
    PortfolioValuationVoidRow,
)
from core.analytics.time_weighted_return import ValuationPoint, validate_valuation_point


_PORTFOLIO_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,63}$")


@dataclass(frozen=True)
class StoredValuationPoint:
    point: ValuationPoint
    source: str
    sequence: int
    created_at: datetime
    voided_at: datetime | None = None
    void_reason: str | None = None


def _canonical_json(value):
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    )


def _content_fingerprint(portfolio):
    content = {
        "cash_history_complete": portfolio.cash_history_complete,
        "migration_warnings": portfolio.migration_warnings,
        "events": [event.to_record() for event in portfolio.transactions],
        "prices": [
            {
                "ticker": asset.ticker,
                "market": asset.market,
                "currency": asset.currency,
                "current_price": repr(float(asset.current_price)),
            }
            for asset in portfolio.assets
        ],
    }
    return hashlib.sha256(_canonical_json(content).encode("utf-8")).hexdigest()


class SQLitePortfolioRepository:
    """SQLite repository for a single local portfolio prototype."""

    def __init__(self, database_path):
        self._sessions = make_session_factory(database_path)

    def portfolio_exists(self, portfolio_id):
        with self._sessions() as session:
            return session.get(PortfolioRow, portfolio_id) is not None

    def import_once(self, portfolio_id, name, portfolio):
        if not isinstance(portfolio_id, str) or not _PORTFOLIO_ID.fullmatch(portfolio_id):
            raise ValueError("Portfolio id must use letters, digits, '_' or '-' (max 64 chars).")
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 120:
            raise ValueError("Portfolio name must contain 1 to 120 characters.")
        if not isinstance(portfolio, Portfolio):
            raise TypeError("portfolio must be a Portfolio instance.")

        fingerprint = _content_fingerprint(portfolio)
        events = [
            ("CASH" if isinstance(event, CashTransaction) else "TRADE", _canonical_json(event.to_record()))
            for event in portfolio.transactions
        ]
        warnings_json = _canonical_json(portfolio.migration_warnings)
        prices = [
            (asset.ticker, asset.market, asset.currency, repr(float(asset.current_price)))
            for asset in portfolio.assets
        ]

        with self._sessions.begin() as session:
            existing = session.get(PortfolioRow, portfolio_id)
            if existing:
                if existing.content_fingerprint == fingerprint:
                    return False
                raise ValueError(
                    "This portfolio id already contains different data; import was not applied."
                )

            session.add(
                PortfolioRow(
                    id=portfolio_id,
                    name=name.strip(),
                    cash_history_complete=portfolio.cash_history_complete,
                    migration_warnings_json=warnings_json,
                    content_fingerprint=fingerprint,
                    created_at=datetime.now(timezone.utc).isoformat(),
                )
            )
            session.flush()
            session.add_all(
                PortfolioEventRow(
                    portfolio_id=portfolio_id,
                    sequence=index,
                    record_type=record_type,
                    event_json=event_json,
                )
                for index, (record_type, event_json) in enumerate(events, start=1)
            )
            session.add_all(
                PortfolioPriceRow(
                    portfolio_id=portfolio_id,
                    ticker=ticker,
                    market=market,
                    currency=currency,
                    current_price=current_price,
                )
                for ticker, market, currency, current_price in prices
            )
        return True

    def get_portfolio(self, portfolio_id):
        with self._sessions() as session:
            row = session.get(PortfolioRow, portfolio_id)
            if row is None:
                return None
            event_rows = session.scalars(
                select(PortfolioEventRow)
                .where(PortfolioEventRow.portfolio_id == portfolio_id)
                .order_by(PortfolioEventRow.sequence)
            ).all()
            price_rows = session.scalars(
                select(PortfolioPriceRow).where(PortfolioPriceRow.portfolio_id == portfolio_id)
            ).all()
            portfolio = replay_transactions([json.loads(item.event_json) for item in event_rows])
            portfolio.cash_history_complete = row.cash_history_complete
            portfolio.migration_warnings = json.loads(row.migration_warnings_json)
            prices = {price.ticker: price for price in price_rows}
            for asset in portfolio.assets:
                stored_price = prices.get(asset.ticker)
                if stored_price is not None:
                    asset.current_price = float(stored_price.current_price)
            return portfolio

    def get_transactions(self, portfolio_id, *, offset, limit):
        portfolio = self.get_portfolio(portfolio_id)
        if portfolio is None:
            return None, []
        events = portfolio.transactions
        return len(events), events[offset : offset + limit]

    def record_valuation_point(self, portfolio_id, point, *, source):
        """Append a timestamped portfolio valuation with its provenance."""
        if not isinstance(portfolio_id, str) or not _PORTFOLIO_ID.fullmatch(portfolio_id):
            raise ValueError("Portfolio id must use letters, digits, '_' or '-' (max 64 chars).")
        validate_valuation_point(point)
        if not isinstance(source, str) or not source.strip() or len(source.strip()) > 120:
            raise ValueError("Valuation source must contain 1 to 120 characters.")

        timestamp = point.timestamp.astimezone(timezone.utc)
        timestamp_text = timestamp.isoformat()
        with self._sessions.begin() as session:
            if session.get(PortfolioRow, portfolio_id) is None:
                raise ValueError("Portfolio does not exist.")
            latest = session.scalar(
                select(PortfolioValuationRow)
                .where(
                    PortfolioValuationRow.portfolio_id == portfolio_id,
                    PortfolioValuationRow.currency == point.currency,
                )
                .order_by(PortfolioValuationRow.sequence.desc())
                .limit(1)
            )
            if latest is not None and timestamp_text <= latest.valuation_at:
                raise ValueError("Valuation timestamp must be later than the latest stored point.")

            sequence = 1 if latest is None else latest.sequence + 1
            created_at = datetime.now(timezone.utc)
            row = PortfolioValuationRow(
                portfolio_id=portfolio_id,
                currency=point.currency,
                sequence=sequence,
                valuation_at=timestamp_text,
                market_value=repr(float(point.market_value)),
                external_flow_after=repr(float(point.external_flow_after)),
                source=source.strip(),
                created_at=created_at.isoformat(),
            )
            session.add(row)
            session.flush()
            return StoredValuationPoint(
                point=ValuationPoint(
                    timestamp=timestamp,
                    market_value=float(point.market_value),
                    currency=point.currency,
                    external_flow_after=float(point.external_flow_after),
                ),
                source=row.source,
                sequence=sequence,
                created_at=created_at,
            )

    def get_valuation_points(self, portfolio_id, *, currency):
        """Return full valuation history, including any append-only void records.

        Returns ``None`` when the portfolio does not exist and an empty list
        when it exists but has no recorded valuation points in that currency.
        """
        if currency not in {"USD", "IRR"}:
            raise ValueError("Currency must be USD or IRR.")
        with self._sessions() as session:
            if session.get(PortfolioRow, portfolio_id) is None:
                return None
            rows = session.execute(
                select(PortfolioValuationRow, PortfolioValuationVoidRow)
                .outerjoin(
                    PortfolioValuationVoidRow,
                    PortfolioValuationVoidRow.valuation_id == PortfolioValuationRow.id,
                )
                .where(
                    PortfolioValuationRow.portfolio_id == portfolio_id,
                    PortfolioValuationRow.currency == currency,
                )
                .order_by(PortfolioValuationRow.sequence)
            ).all()
            return [
                StoredValuationPoint(
                    point=ValuationPoint(
                        timestamp=datetime.fromisoformat(row.valuation_at),
                        market_value=float(row.market_value),
                        currency=row.currency,
                        external_flow_after=float(row.external_flow_after),
                    ),
                    source=row.source,
                    sequence=row.sequence,
                    created_at=datetime.fromisoformat(row.created_at),
                    voided_at=(
                        datetime.fromisoformat(void_row.voided_at) if void_row is not None else None
                    ),
                    void_reason=void_row.reason if void_row is not None else None,
                )
                for row, void_row in rows
            ]

    def void_valuation_point(self, portfolio_id, *, currency, sequence, reason):
        """Append a correction marker; the original valuation remains immutable."""
        if not isinstance(portfolio_id, str) or not _PORTFOLIO_ID.fullmatch(portfolio_id):
            raise ValueError("Portfolio id must use letters, digits, '_' or '-' (max 64 chars).")
        if currency not in {"USD", "IRR"}:
            raise ValueError("Currency must be USD or IRR.")
        if isinstance(sequence, bool) or not isinstance(sequence, int) or sequence < 1:
            raise ValueError("Valuation sequence must be a positive integer.")
        if not isinstance(reason, str) or not reason.strip() or len(reason.strip()) > 250:
            raise ValueError("Correction reason must contain 1 to 250 characters.")

        with self._sessions.begin() as session:
            row = session.scalar(
                select(PortfolioValuationRow).where(
                    PortfolioValuationRow.portfolio_id == portfolio_id,
                    PortfolioValuationRow.currency == currency,
                    PortfolioValuationRow.sequence == sequence,
                )
            )
            if row is None:
                raise ValueError("Valuation point was not found.")
            if session.scalar(
                select(PortfolioValuationVoidRow.id).where(
                    PortfolioValuationVoidRow.valuation_id == row.id
                )
            ) is not None:
                raise ValueError("Valuation point has already been voided.")
            correction = PortfolioValuationVoidRow(
                valuation_id=row.id,
                reason=reason.strip(),
                voided_at=datetime.now(timezone.utc).isoformat(),
            )
            session.add(correction)
            session.flush()
            return StoredValuationPoint(
                point=ValuationPoint(
                    timestamp=datetime.fromisoformat(row.valuation_at),
                    market_value=float(row.market_value),
                    currency=row.currency,
                    external_flow_after=float(row.external_flow_after),
                ),
                source=row.source,
                sequence=row.sequence,
                created_at=datetime.fromisoformat(row.created_at),
                voided_at=datetime.fromisoformat(correction.voided_at),
                void_reason=correction.reason,
            )
