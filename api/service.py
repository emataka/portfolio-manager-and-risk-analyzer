import logging
import math
import os
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.exc import SQLAlchemyError

from api.repository import SQLitePortfolioRepository
from core.analytics.time_weighted_return import calculate_time_weighted_return
from core.models.cash_transaction import CashTransaction


logger = logging.getLogger(__name__)


def _database_settings():
    database_path = os.environ.get("PORTFOLIO_API_DB", "").strip()
    portfolio_id = os.environ.get("PORTFOLIO_API_PORTFOLIO_ID", "local").strip()
    if not database_path:
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_configured",
                "message": "Set PORTFOLIO_API_DB to the local SQLite database file.",
            },
        )
    return Path(database_path).expanduser(), portfolio_id


def configured_portfolio_exists():
    try:
        database_path, portfolio_id = _database_settings()
        if not database_path.is_file():
            return False
        return SQLitePortfolioRepository(database_path).portfolio_exists(portfolio_id)
    except (HTTPException, OSError, SQLAlchemyError, ValueError):
        return False


def load_configured_portfolio():
    database_path, portfolio_id = _database_settings()
    if not database_path.is_file():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_initialized",
                "message": "Run the JSON import command to create and populate the local database.",
            },
        )
    try:
        portfolio = SQLitePortfolioRepository(database_path).get_portfolio(portfolio_id)
    except (OSError, SQLAlchemyError, TypeError, ValueError) as error:
        logger.exception("Unable to load portfolio from SQLite database")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "portfolio_unavailable",
                "message": "The local portfolio database is unreadable or invalid.",
            },
        ) from error
    if portfolio is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "portfolio_not_found",
                "message": "The configured portfolio id was not found in the local database.",
            },
        )
    return portfolio


def load_configured_transactions(*, offset, limit):
    database_path, portfolio_id = _database_settings()
    if not database_path.is_file():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_initialized",
                "message": "Run the JSON import command to create and populate the local database.",
            },
        )
    try:
        total, transactions = SQLitePortfolioRepository(database_path).get_transactions(
            portfolio_id,
            offset=offset,
            limit=limit,
        )
    except (OSError, SQLAlchemyError, TypeError, ValueError) as error:
        logger.exception("Unable to load portfolio transactions from SQLite database")
        raise HTTPException(
            status_code=503,
            detail={"code": "portfolio_unavailable", "message": "Portfolio data is unavailable."},
        ) from error
    if total is None:
        raise HTTPException(
            status_code=404,
            detail={
                "code": "portfolio_not_found",
                "message": "The configured portfolio id was not found in the local database.",
            },
        )
    return total, transactions


def load_configured_valuation_performance(currencies):
    database_path, portfolio_id = _database_settings()
    if not database_path.is_file():
        raise HTTPException(
            status_code=503,
            detail={
                "code": "database_not_initialized",
                "message": "Run the database migration before reading valuation history.",
            },
        )
    try:
        repository = SQLitePortfolioRepository(database_path)
        result = {}
        for currency in currencies:
            records = repository.get_valuation_points(portfolio_id, currency=currency)
            if records is None:
                raise HTTPException(
                    status_code=404,
                    detail={
                        "code": "portfolio_not_found",
                        "message": "The configured portfolio id was not found in the local database.",
                    },
                )
            result[currency] = _build_valuation_performance(records)
        return result
    except HTTPException:
        raise
    except (OSError, SQLAlchemyError, TypeError, ValueError) as error:
        logger.exception("Unable to load portfolio valuation history from SQLite database")
        raise HTTPException(
            status_code=503,
            detail={
                "code": "valuation_history_unavailable",
                "message": "Valuation history is unavailable; check that database migrations are current.",
            },
        ) from error


def _build_valuation_performance(records):
    active = [record for record in records if record.voided_at is None]
    voided_count = len(records) - len(active)
    sources = list(dict.fromkeys(record.source for record in active))
    empty = {
        "total_return_percentage": None,
        "observations_count": len(active),
        "voided_observations_count": voided_count,
        "start_at": active[0].point.timestamp if active else None,
        "end_at": active[-1].point.timestamp if active else None,
        "sources": sources,
    }

    if len(active) < 2:
        return {
            **empty,
            "status": "insufficient_data",
            "warnings": ["At least two non-voided valuation points are required for TWR."],
        }
    if active[-1].point.external_flow_after != 0:
        return {
            **empty,
            "status": "insufficient_data",
            "warnings": ["The latest valuation has an external flow after it; record a later valuation."],
        }

    try:
        total_return = calculate_time_weighted_return([record.point for record in active])
        total_return_percentage = total_return * 100
        if not math.isfinite(total_return_percentage):
            raise ValueError("TWR percentage exceeded the finite numeric range.")
    except ValueError as error:
        return {
            **empty,
            "status": "unavailable",
            "warnings": [str(error)],
        }
    return {
        **empty,
        "status": "available",
        "total_return_percentage": total_return_percentage,
        "warnings": [],
    }


def build_portfolio_view(portfolio):
    report = portfolio.report()
    risk_by_ticker = {item["ticker"]: item["level"] for item in portfolio.risk_check()}
    assets = [
        {
            "ticker": asset["ticker"],
            "market": asset["market"],
            "currency": asset["currency"],
            "quantity": asset["quantity"],
            "buy_price": asset["buy_price"],
            "current_price": asset["current_price"],
            "value": asset["value"],
            "profit_loss": asset["profit_loss"],
            "weight": asset["currency_weight"],
            "risk_level": risk_by_ticker[asset["ticker"]],
        }
        for asset in report["assets"]
    ]
    warnings = list(portfolio.migration_warnings)
    if not portfolio.cash_history_complete:
        warnings.append("Cash history is incomplete; total value may not reflect broker cash.")
    warnings.append(
        "Price timestamps are unavailable in this prototype; current prices may be stale."
    )
    return {
        "assets": assets,
        "currencies": report["currencies"],
        "cash_history_complete": portfolio.cash_history_complete,
        "price_timestamp_available": False,
        "warnings": list(dict.fromkeys(warnings)),
    }


def serialize_transaction(transaction):
    if isinstance(transaction, CashTransaction):
        return {
            "record_type": "CASH",
            "side": transaction.side,
            "currency": transaction.currency,
            "amount": transaction.amount,
            "executed_at": transaction.executed_at,
        }
    return {
        "record_type": "TRADE",
        "side": transaction.side,
        "ticker": transaction.ticker,
        "market": transaction.market,
        "currency": transaction.currency,
        "quantity": transaction.quantity,
        "price": transaction.price,
        "fees": transaction.fees,
        "executed_at": transaction.executed_at,
    }
