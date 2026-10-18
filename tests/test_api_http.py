from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from api.database import run_migrations
from api.main import app
from api.repository import SQLitePortfolioRepository
from core.models.portfolio import Portfolio


@pytest.fixture
def client_with_portfolio(tmp_path, monkeypatch):
    database_path = tmp_path / "portfolio.sqlite3"
    run_migrations(database_path)

    portfolio = Portfolio()
    first = datetime(2025, 1, 1, tzinfo=timezone.utc)
    portfolio.record_cash("OPENING_CASH", 500, "USD", executed_at=first)
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100, current_price=125, executed_at=first
    )
    portfolio.record_buy(
        "AAPL", "US", 1, 110, fees=2,
        executed_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )
    SQLitePortfolioRepository(database_path).import_once(
        "local", "Personal portfolio", portfolio
    )

    monkeypatch.setenv("PORTFOLIO_API_DB", str(database_path))
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "local")
    with TestClient(app) as client:
        yield client


def test_http_health_and_portfolio_response(client_with_portfolio):
    health = client_with_portfolio.get("/health")
    response = client_with_portfolio.get("/api/v1/portfolio")

    assert health.status_code == 200
    assert health.json() == {"status": "ok", "portfolio_configured": True}
    assert response.status_code == 200
    body = response.json()
    assert body["assets"][0]["ticker"] == "AAPL"
    assert body["assets"][0]["current_price"] == pytest.approx(125)
    assert body["currencies"]["USD"]["cash_balance"] == pytest.approx(388)
    assert body["price_timestamp_available"] is False
    assert body["performance"]["USD"]["status"] == "insufficient_data"
    assert body["performance"]["USD"]["observations_count"] == 0


def test_http_transaction_pagination_and_query_validation(client_with_portfolio):
    response = client_with_portfolio.get(
        "/api/v1/portfolio/transactions", params={"limit": 2, "offset": 1}
    )
    invalid_limit = client_with_portfolio.get(
        "/api/v1/portfolio/transactions", params={"limit": 101}
    )

    assert response.status_code == 200
    page = response.json()
    assert page["total"] == 3
    assert page["offset"] == 1
    assert [item["side"] for item in page["items"]] == ["OPENING_BALANCE", "BUY"]
    assert invalid_limit.status_code == 422


def test_http_returns_not_found_for_unconfigured_portfolio_id(
    client_with_portfolio, monkeypatch
):
    monkeypatch.setenv("PORTFOLIO_API_PORTFOLIO_ID", "missing")

    response = client_with_portfolio.get("/api/v1/portfolio")

    assert response.status_code == 404
    assert response.json()["detail"]["code"] == "portfolio_not_found"


def test_http_returns_service_unavailable_when_database_is_not_configured(monkeypatch):
    monkeypatch.delenv("PORTFOLIO_API_DB", raising=False)
    monkeypatch.delenv("PORTFOLIO_API_PORTFOLIO_ID", raising=False)

    with TestClient(app) as client:
        response = client.get("/api/v1/portfolio")

    assert response.status_code == 503
    assert response.json()["detail"]["code"] == "database_not_configured"
