import csv
from datetime import datetime, timezone

import pytest

from core.import_export.transaction_csv import (
    CSV_FIELDS,
    apply_transactions_csv_import,
    export_transactions_csv,
    preview_transactions_csv,
    write_transactions_csv_template,
)
from core.models.portfolio import Portfolio


def _write_csv(path, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=CSV_FIELDS, lineterminator="\r\n")
        writer.writeheader()
        writer.writerows(rows)


def _trade_row(side, *, ticker="AAPL", quantity="2", price="100", executed_at="2025-01-01T00:00:00+00:00"):
    return {
        "record_type": "TRADE",
        "side": side,
        "ticker": ticker,
        "market": "US",
        "quantity": quantity,
        "price": price,
        "fees": "0",
        "amount": "",
        "currency": "USD",
        "executed_at": executed_at,
    }


def test_exported_ledger_import_is_idempotent(tmp_path):
    portfolio = Portfolio()
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100,
        executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    portfolio.record_sell(
        "AAPL", "US", 1, 120,
        executed_at=datetime(2025, 1, 2, tzinfo=timezone.utc),
    )
    path = tmp_path / "transactions.csv"

    export_transactions_csv(portfolio, path)
    preview = preview_transactions_csv(portfolio, path)

    assert preview.errors == ()
    assert preview.importable_count == 0
    assert preview.duplicate_rows == (2, 3)
    assert apply_transactions_csv_import(portfolio, preview) == 0
    assert len(portfolio.transactions) == 2
    assert portfolio.assets[0].quantity == pytest.approx(1)


def test_import_applies_valid_trade_and_cash_rows(tmp_path):
    path = tmp_path / "valid.csv"
    timestamp = "2025-01-01T00:00:00+00:00"
    cash_row = {
        "record_type": "CASH", "side": "OPENING_CASH", "ticker": "", "market": "",
        "quantity": "", "price": "", "fees": "", "amount": "5000",
        "currency": "USD", "executed_at": timestamp,
    }
    _write_csv(path, [cash_row, _trade_row("OPENING_BALANCE", executed_at=timestamp)])
    portfolio = Portfolio()

    preview = preview_transactions_csv(portfolio, path)

    assert preview.errors == ()
    assert preview.importable_count == 2
    assert apply_transactions_csv_import(portfolio, preview) == 2
    assert portfolio.assets[0].quantity == pytest.approx(2)
    assert portfolio._cash_balances()["USD"] == pytest.approx(5000)


def test_invalid_later_row_rejects_entire_batch_without_mutation(tmp_path):
    path = tmp_path / "invalid-ledger.csv"
    _write_csv(path, [
        _trade_row("OPENING_BALANCE"),
        _trade_row("SELL", quantity="3", price="120", executed_at="2025-01-02T00:00:00+00:00"),
    ])
    portfolio = Portfolio()

    preview = preview_transactions_csv(portfolio, path)

    assert preview.errors
    assert "only 2.0 shares are held" in preview.errors[0]
    assert preview.events == ()
    assert portfolio.transactions == []
    with pytest.raises(ValueError, match="contains errors"):
        apply_transactions_csv_import(portfolio, preview)
    assert portfolio.transactions == []


def test_import_preview_cannot_be_applied_after_portfolio_changes(tmp_path):
    path = tmp_path / "one-opening.csv"
    _write_csv(path, [_trade_row("OPENING_BALANCE")])
    portfolio = Portfolio()
    preview = preview_transactions_csv(portfolio, path)
    portfolio.record_cash("OPENING_CASH", 100, "USD")

    with pytest.raises(ValueError, match="Portfolio changed after preview"):
        apply_transactions_csv_import(portfolio, preview)
    assert len(portfolio.transactions) == 1


def test_template_can_be_imported_into_an_empty_portfolio(tmp_path):
    path = tmp_path / "template.csv"
    write_transactions_csv_template(path)
    portfolio = Portfolio()

    preview = preview_transactions_csv(portfolio, path)

    assert preview.errors == ()
    assert preview.importable_count == 2
    assert apply_transactions_csv_import(portfolio, preview) == 2
    assert portfolio.assets[0].ticker == "نماد"
    assert portfolio._cash_balances()["IRR"] == pytest.approx(1_000_000)


def test_csv_import_rejects_mismatched_headers(tmp_path):
    path = tmp_path / "bad-header.csv"
    path.write_text("ticker,quantity\nAAPL,2\n", encoding="utf-8")

    with pytest.raises(ValueError, match="headers do not match"):
        preview_transactions_csv(Portfolio(), path)
