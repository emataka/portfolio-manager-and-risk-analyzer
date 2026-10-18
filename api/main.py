from datetime import datetime, timezone

from fastapi import FastAPI, Query

from api.schemas import HealthResponse, PortfolioView, TransactionPage
from api.service import (
    build_portfolio_view,
    configured_portfolio_exists,
    load_configured_portfolio,
    load_configured_transactions,
    load_configured_valuation_performance,
    serialize_transaction,
)


app = FastAPI(
    title="Portfolio Manager API",
    description=(
        "Local, read-only API for viewing one portfolio loaded from a configured SQLite file. "
        "It is a development prototype and does not provide authentication."
    ),
    version="0.1.0",
)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health():
    return {
        "status": "ok",
        "portfolio_configured": configured_portfolio_exists(),
    }


@app.get("/api/v1/portfolio", response_model=PortfolioView, tags=["portfolio"])
def get_portfolio():
    portfolio = load_configured_portfolio()
    portfolio_view = build_portfolio_view(portfolio)
    return {
        **portfolio_view,
        "performance": load_configured_valuation_performance(
            portfolio_view["currencies"].keys()
        ),
        "generated_at": datetime.now(timezone.utc),
    }


@app.get("/api/v1/portfolio/transactions", response_model=TransactionPage, tags=["portfolio"])
def get_transactions(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    total, page = load_configured_transactions(offset=offset, limit=limit)
    return {
        "total": total,
        "offset": offset,
        "limit": limit,
        "items": [serialize_transaction(transaction) for transaction in page],
    }
