import json
from datetime import datetime, timezone

import pytest

from core.models.asset import Asset
from core.models.portfolio import Portfolio
from core.persistence.portfolio_store import load_portfolio, save_portfolio


def test_save_and_load_round_trip_keeps_prices_and_unicode_tickers(tmp_path):
    original = Portfolio()
    original.add_asset(Asset("AAPL", 2.5, 100, "US", current_price=115))
    original.add_asset(Asset("وبملت", 10, 5000, "IR", current_price=5200))
    path = tmp_path / "portfolio.json"

    save_portfolio(original, path)
    loaded = load_portfolio(path)

    assert [(a.ticker, a.quantity, a.buy_price, a.current_price, a.market, a.currency) for a in loaded.assets] == [
        ("AAPL", 2.5, 100, 115, "US", "USD"),
        ("وبملت", 10, 5000, 5200, "IR", "IRR"),
    ]


def test_empty_portfolio_can_be_saved_and_loaded(tmp_path):
    path = tmp_path / "empty.json"

    save_portfolio(Portfolio(), path)

    assert load_portfolio(path).assets == []


def test_save_refuses_to_overwrite_unless_explicitly_allowed(tmp_path):
    path = tmp_path / "portfolio.json"
    first = Portfolio()
    first.add_asset(Asset("AAPL", 1, 100, "US"))
    save_portfolio(first, path)

    with pytest.raises(FileExistsError):
        save_portfolio(Portfolio(), path)

    save_portfolio(Portfolio(), path, overwrite=True)
    assert load_portfolio(path).assets == []


@pytest.mark.parametrize(
    "document, message",
    [
        ({"schema_version": 99, "assets": []}, "Unsupported portfolio schema"),
        ({"schema_version": 3, "assets": {}}, "assets list"),
        (
            {
                "schema_version": 3,
                "assets": [
                    {
                        "ticker": "AAPL",
                        "quantity": float("nan"),
                        "buy_price": 100,
                        "current_price": 100,
                        "market": "US",
                        "currency": "USD",
                    }
                ],
                "transactions": [],
            },
            "finite and greater than zero",
        ),
    ],
)
def test_load_rejects_unsupported_or_invalid_documents(tmp_path, document, message):
    path = tmp_path / "invalid.json"
    path.write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(ValueError, match=message):
        load_portfolio(path)


def test_load_rejects_duplicate_assets_and_invalid_json(tmp_path):
    path = tmp_path / "duplicate.json"
    asset = {
        "ticker": "AAPL",
        "quantity": 1,
        "buy_price": 100,
        "current_price": 100,
        "market": "US",
        "currency": "USD",
    }
    path.write_text(
        json.dumps({"schema_version": 2, "assets": [asset, asset]}),
        encoding="utf-8",
    )
    with pytest.raises(ValueError, match="already exists"):
        load_portfolio(path)

    path.write_text("{not valid json", encoding="utf-8")
    with pytest.raises(ValueError, match="invalid JSON"):
        load_portfolio(path)


def test_schema_v1_migrates_currency_from_market(tmp_path):
    path = tmp_path / "legacy.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "assets": [
                    {
                        "ticker": "AAPL",
                        "quantity": 1,
                        "buy_price": 100,
                        "current_price": 110,
                        "market": "US",
                    },
                    {
                        "ticker": "وبملت",
                        "quantity": 1,
                        "buy_price": 5000,
                        "current_price": 5200,
                        "market": "IR",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    loaded = load_portfolio(path)

    assert [asset.currency for asset in loaded.assets] == ["USD", "IRR"]
    assert any("Verify legacy purchase-price units" in warning for warning in loaded.migration_warnings)


def test_schema_v2_rejects_currency_that_conflicts_with_market(tmp_path):
    path = tmp_path / "wrong-currency.json"
    path.write_text(
        json.dumps(
            {
                "schema_version": 2,
                "assets": [
                    {
                        "ticker": "وبملت",
                        "quantity": 1,
                        "buy_price": 5000,
                        "current_price": 5200,
                        "market": "IR",
                        "currency": "IRT",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="quotes prices in IRR"):
        load_portfolio(path)


def test_schema_v4_round_trip_preserves_transaction_history_cash_and_accounting(tmp_path):
    portfolio = Portfolio()
    portfolio.record_cash(
        "OPENING_CASH", 1000, "USD",
        executed_at=datetime(2024, 12, 31, tzinfo=timezone.utc),
    )
    portfolio.record_opening_balance(
        "AAPL", "US", 10, 100,
        executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    portfolio.record_buy(
        "AAPL", "US", 10, 120, fees=20,
        executed_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )
    portfolio.record_sell(
        "AAPL", "US", 5, 130, fees=10,
        executed_at=datetime(2025, 1, 3, tzinfo=timezone.utc),
    )
    portfolio.assets[0].update_price(125)
    path = tmp_path / "ledger.json"

    save_portfolio(portfolio, path)
    loaded = load_portfolio(path)

    assert [transaction.side for transaction in loaded.transactions] == [
        "OPENING_CASH", "OPENING_BALANCE", "BUY", "SELL"
    ]
    assert loaded.assets[0].quantity == 15
    assert loaded.assets[0].buy_price == pytest.approx(111)
    assert loaded.assets[0].current_price == 125
    assert loaded.realized_profit_loss_by_currency["USD"] == pytest.approx(85)
    assert loaded.report()["currencies"]["USD"]["profit_loss"] == pytest.approx(295)
    assert loaded.report()["currencies"]["USD"]["cash_balance"] == pytest.approx(420)
    assert loaded.report()["currencies"]["USD"]["total_value"] == pytest.approx(2295)


def test_schema_v3_transaction_snapshot_remains_loadable(tmp_path):
    path = tmp_path / "schema-v3.json"
    portfolio = Portfolio()
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100,
        executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    save_portfolio(portfolio, path)
    document = json.loads(path.read_text(encoding="utf-8"))
    document["schema_version"] = 3
    document["transactions"] = [
        {key: value for key, value in row.items() if key != "type"}
        for row in document["transactions"]
    ]
    path.write_text(json.dumps(document), encoding="utf-8")

    loaded = load_portfolio(path)
    assert loaded.assets[0].quantity == 2
    assert loaded._cash_balances() == {}
    assert loaded.cash_history_complete is False
    assert any("Cash history is incomplete" in warning for warning in loaded.migration_warnings)
    assert loaded.report()["currencies"]["USD"]["cumulative_return_percentage"] is None
