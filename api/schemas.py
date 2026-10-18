from datetime import datetime
from typing import Literal

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: Literal["ok"]
    portfolio_configured: bool


class AssetView(BaseModel):
    ticker: str
    market: str
    currency: str
    quantity: float
    buy_price: float
    current_price: float
    value: float
    profit_loss: float
    weight: float
    risk_level: Literal["ok", "warning", "high"]


class CurrencySummary(BaseModel):
    total_value: float
    securities_value: float
    cash_balance: float
    cost_basis: float
    net_contributions: float
    realized_profit_loss: float
    unrealized_profit_loss: float
    profit_loss: float
    unrealized_return_percentage: float | None
    cumulative_return_percentage: float | None


class ValuationPerformanceView(BaseModel):
    status: Literal["available", "insufficient_data", "unavailable"]
    total_return_percentage: float | None
    observations_count: int
    voided_observations_count: int
    start_at: datetime | None
    end_at: datetime | None
    sources: list[str]
    warnings: list[str]


class PortfolioView(BaseModel):
    generated_at: datetime
    assets: list[AssetView]
    currencies: dict[str, CurrencySummary]
    performance: dict[str, ValuationPerformanceView]
    cash_history_complete: bool
    price_timestamp_available: Literal[False] = False
    warnings: list[str]


class TransactionView(BaseModel):
    record_type: Literal["TRADE", "CASH"]
    side: str
    ticker: str | None = None
    market: str | None = None
    currency: str
    quantity: float | None = None
    price: float | None = None
    fees: float | None = None
    amount: float | None = None
    executed_at: datetime


class TransactionPage(BaseModel):
    total: int
    offset: int
    limit: int
    items: list[TransactionView]
