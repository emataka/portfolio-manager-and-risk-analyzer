import sqlite3
from datetime import datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy import func, select

from api.database import make_session_factory, run_migrations
from api.main import get_portfolio, get_transactions
from api.models import PortfolioEventRow
from api.repository import SQLitePortfolioRepository
from api.schemas import PortfolioView, TransactionPage
from core.analytics.time_weighted_return import ValuationPoint
from core.models.portfolio import Portfolio
from core.persistence.portfolio_store import load_portfolio, save_portfolio


@pytest.fixture
def database_path(tmp_path):
    path = tmp_path / "portfolio.sqlite3"
    run_migrations(path)
    return path


def sample_portfolio():
    portfolio = Portfolio()
    first = datetime(2025, 1, 1, tzinfo=timezone.utc)
    second = datetime(2025, 1, 2, tzinfo=timezone.utc)
    portfolio.record_cash("OPENING_CASH", 500, "USD", executed_at=first)
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100, current_price=125, executed_at=first
    )
    portfolio.record_buy("AAPL", "US", 1, 110, fees=2, executed_at=second)
    return portfolio


def test_json_import_and_sqlite_repository_round_trip(tmp_path, database_path):
    source = tmp_path / "portfolio.json"
    save_portfolio(sample_portfolio(), source)
    imported = load_portfolio(source)
    repository = SQLitePortfolioRepository(database_path)

    assert repository.import_once("local", "Personal portfolio", imported) is True
    restored = repository.get_portfolio("local")

    assert [(item.ticker, item.quantity, item.buy_price, item.current_price) for item in restored.assets] == [
        ("AAPL", 3, pytest.approx(104), 125)
    ]
    assert [event.to_record() for event in restored.transactions] == [
        event.to_record() for event in imported.transactions
    ]
    assert restored.report()["currencies"]["USD"]["cash_balance"] == pytest.approx(388)
    assert restored.cash_history_complete is True


def test_import_once_is_idempotent_and_rejects_different_snapshot(database_path):
    repository = SQLitePortfolioRepository(database_path)
    portfolio = sample_portfolio()

    assert repository.import_once("local", "Personal portfolio", portfolio) is True
    assert repository.import_once("local", "Personal portfolio", portfolio) is False
    with make_session_factory(database_path)() as session:
        count = session.scalar(select(func.count()).select_from(PortfolioEventRow))
    assert count == 3

    changed = sample_portfolio()
    changed.assets[0].current_price = 126
    with pytest.raises(ValueError, match="already contains different data"):
        repository.import_once("local", "Personal portfolio", changed)


@pytest.mark.parametrize("statement", [
    "UPDATE portfolio_events SET event_json = '{}' WHERE id = 1",
    "DELETE FROM portfolio_events WHERE id = 1",
])
def test_sqlite_ledger_events_are_append_only(database_path, statement):
    SQLitePortfolioRepository(database_path).import_once("local", "Personal portfolio", sample_portfolio())

    connection = sqlite3.connect(database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(statement)
    finally:
        connection.close()


def test_api_returns_validated_portfolio_and_paginated_transactions(database_path, monkeypatch):
    SQLitePortfolioRepository(database_path).import_once("local", "Personal portfolio", sample_portfolio())
    monkeypatch.setenv("PORTFOLIO_API_DB", str(database_path))
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "local")

    portfolio_response = PortfolioView.model_validate(get_portfolio())
    transaction_response = TransactionPage.model_validate(get_transactions(limit=2, offset=1))

    assert portfolio_response.assets[0].ticker == "AAPL"
    assert portfolio_response.assets[0].current_price == pytest.approx(125)
    assert portfolio_response.currencies["USD"].cash_balance == pytest.approx(388)
    assert portfolio_response.price_timestamp_available is False
    assert portfolio_response.performance["USD"].status == "insufficient_data"
    assert portfolio_response.performance["USD"].total_return_percentage is None
    assert transaction_response.total == 3
    assert transaction_response.offset == 1
    assert [item.side for item in transaction_response.items] == ["OPENING_BALANCE", "BUY"]


def test_api_reports_missing_portfolio_as_not_found(database_path, monkeypatch):
    monkeypatch.setenv("PORTFOLIO_API_DB", str(database_path))
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "missing")

    with pytest.raises(HTTPException) as error:
        get_portfolio()

    assert error.value.status_code == 404
    assert error.value.detail["code"] == "portfolio_not_found"


def test_valuation_void_is_audited_and_retains_original_point(database_path):
    repository = SQLitePortfolioRepository(database_path)
    repository.import_once("local", "Personal portfolio", sample_portfolio())
    point = ValuationPoint(datetime(2025, 1, 1, tzinfo=timezone.utc), 0, "USD")
    repository.record_valuation_point("local", point, source="test input")

    correction = repository.void_valuation_point(
        "local", currency="USD", sequence=1, reason="Test data; not a real valuation"
    )
    history = repository.get_valuation_points("local", currency="USD")

    assert correction.void_reason == "Test data; not a real valuation"
    assert len(history) == 1
    assert history[0].point.market_value == 0
    assert history[0].source == "test input"
    assert history[0].voided_at is not None
    assert history[0].void_reason == correction.void_reason
    with pytest.raises(ValueError, match="already been voided"):
        repository.void_valuation_point(
            "local", currency="USD", sequence=1, reason="Duplicate correction"
        )


def test_api_performance_excludes_voided_valuations(database_path, monkeypatch):
    repository = SQLitePortfolioRepository(database_path)
    repository.import_once("local", "Personal portfolio", sample_portfolio())
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 1, 1, tzinfo=timezone.utc), 0, "USD"),
        source="test data",
    )
    repository.void_valuation_point("local", currency="USD", sequence=1, reason="Test input")
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 1, 2, tzinfo=timezone.utc), 1000, "USD"),
        source="broker statement",
    )
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 2, 2, tzinfo=timezone.utc), 1100, "USD"),
        source="broker statement",
    )
    monkeypatch.setenv("PORTFOLIO_API_DB", str(database_path))
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "local")

    response = PortfolioView.model_validate(get_portfolio())
    performance = response.performance["USD"]

    assert performance.status == "available"
    assert performance.total_return_percentage == pytest.approx(10)
    assert performance.observations_count == 2
    assert performance.voided_observations_count == 1
    assert performance.sources == ["broker statement"]


def test_api_performance_waits_for_valuation_after_final_external_flow(database_path, monkeypatch):
    repository = SQLitePortfolioRepository(database_path)
    repository.import_once("local", "Personal portfolio", sample_portfolio())
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 1, 1, tzinfo=timezone.utc), 1000, "USD", 100),
        source="broker statement",
    )
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 2, 1, tzinfo=timezone.utc), 1150, "USD", 50),
        source="broker statement",
    )
    monkeypatch.setenv("PORTFOLIO_API_DB", str(database_path))
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "local")

    response = PortfolioView.model_validate(get_portfolio())
    performance = response.performance["USD"]

    assert performance.status == "insufficient_data"
    assert performance.total_return_percentage is None
    assert performance.observations_count == 2
    assert "record a later valuation" in performance.warnings[0]


def test_valuation_correction_records_are_append_only(database_path):
    repository = SQLitePortfolioRepository(database_path)
    repository.import_once("local", "Personal portfolio", sample_portfolio())
    repository.record_valuation_point(
        "local",
        ValuationPoint(datetime(2025, 1, 1, tzinfo=timezone.utc), 0, "USD"),
        source="test input",
    )
    repository.void_valuation_point(
        "local", currency="USD", sequence=1, reason="Test data"
    )
    connection = sqlite3.connect(database_path)
    try:
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute(
                "UPDATE portfolio_valuation_voids SET reason = 'changed' WHERE id = 1"
            )
        with pytest.raises(sqlite3.IntegrityError, match="append-only"):
            connection.execute("DELETE FROM portfolio_valuation_voids WHERE id = 1")
    finally:
        connection.close()
