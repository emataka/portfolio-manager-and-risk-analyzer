import numpy as np
import pandas as pd
import pytest

from core.data.providers import ir_market, us_market
from core.data.providers.ir_market import IranMarketProvider
from core.data.providers.us_market import USMarketProvider


class FakeUSStock:
    def __init__(self, history):
        self._history = history
        self.requested_periods = []

    def history(self, period):
        self.requested_periods.append(period)
        return self._history


def test_us_provider_normalizes_ticker_and_returns_close(monkeypatch):
    history = pd.DataFrame(
        {"Close": [101.5, 102.0]},
        index=pd.date_range("2025-01-01", periods=2),
    )
    stock = FakeUSStock(history)
    requested_tickers = []
    monkeypatch.setattr(
        us_market.yf,
        "Ticker",
        lambda ticker: requested_tickers.append(ticker) or stock,
    )

    assert USMarketProvider().get_price("aapl") == 101.5
    assert USMarketProvider.currency == "USD"
    assert requested_tickers == ["AAPL"]
    assert stock.requested_periods == ["1d"]


def test_us_provider_rejects_empty_history(monkeypatch):
    monkeypatch.setattr(
        us_market.yf,
        "Ticker",
        lambda ticker: FakeUSStock(pd.DataFrame()),
    )

    with pytest.raises(ValueError, match="not found"):
        USMarketProvider().get_price_history("AAPL", years=2)


def test_iran_provider_returns_recent_close_history(monkeypatch):
    history = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=300),
            "close": np.arange(300, dtype=float) + 100,
        }
    )
    stock = type("FakeIranStock", (), {"history": history, "last_price": 399.0})()
    requested_tickers = []
    monkeypatch.setattr(
        ir_market.tse,
        "Ticker",
        lambda ticker: requested_tickers.append(ticker) or stock,
    )

    prices = IranMarketProvider().get_price_history("فولاد", years=1)

    assert requested_tickers == ["فولاد"]
    assert len(prices) == 252
    assert prices.iloc[0] == 148
    assert prices.iloc[-1] == 399
    assert prices.index.name == "date"
    assert IranMarketProvider.currency == "IRR"


def test_iran_provider_translates_unknown_ticker(monkeypatch):
    def missing_ticker(_ticker):
        raise ValueError("provider error")

    monkeypatch.setattr(ir_market.tse, "Ticker", missing_ticker)

    with pytest.raises(ValueError, match="Ticker 'UNKNOWN' not found"):
        IranMarketProvider().get_price("UNKNOWN")
