from datetime import datetime, timezone

import pytest

from core.models.asset import Asset
from core.models.portfolio import Portfolio


def test_weighted_average_cost_includes_buy_fees_and_sell_fees():
    portfolio = Portfolio()
    portfolio.record_opening_balance(
        "AAPL",
        "US",
        10,
        100,
        current_price=125,
        executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc),
    )
    bought_at = datetime(2025, 1, 2, tzinfo=timezone.utc)
    sold_at = datetime(2025, 1, 3, tzinfo=timezone.utc)

    portfolio.record_buy("AAPL", "US", 10, 120, fees=20, executed_at=bought_at)
    realized = portfolio.record_sell(
        "AAPL", "US", 5, 130, fees=10, executed_at=sold_at
    )

    asset = portfolio.assets[0]
    assert asset.quantity == 15
    assert asset.buy_price == pytest.approx(111)
    assert realized == pytest.approx(85)
    assert portfolio.report()["currencies"]["USD"]["unrealized_profit_loss"] == pytest.approx(210)
    assert portfolio.report()["currencies"]["USD"]["profit_loss"] == pytest.approx(295)
    assert portfolio.report()["currencies"]["USD"]["realized_profit_loss"] == pytest.approx(85)
    assert portfolio.report()["currencies"]["USD"]["cumulative_return_percentage"] == pytest.approx(29.5)


def test_sell_rejects_quantity_above_position_without_mutating_portfolio():
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 2, 100, "US"))
    transaction_count = len(portfolio.transactions)

    with pytest.raises(ValueError, match="only 2 shares are held"):
        portfolio.record_sell("AAPL", "US", 3, 110)

    assert portfolio.assets[0].quantity == 2
    assert len(portfolio.transactions) == transaction_count


def test_transactions_must_be_recorded_chronologically():
    portfolio = Portfolio()
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100, executed_at=datetime(2025, 1, 2, tzinfo=timezone.utc)
    )

    with pytest.raises(ValueError, match="chronological order"):
        portfolio.record_buy(
            "AAPL", "US", 1, 110, executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
        )


def test_fully_sold_position_keeps_realized_pnl_without_dividing_by_zero():
    portfolio = Portfolio()
    portfolio.record_opening_balance(
        "AAPL", "US", 2, 100, executed_at=datetime(2025, 1, 1, tzinfo=timezone.utc)
    )

    realized = portfolio.record_sell("AAPL", "US", 2, 120, fees=5)
    currency_report = portfolio.report()["currencies"]["USD"]

    assert portfolio.assets == []
    assert realized == pytest.approx(35)
    assert currency_report["total_value"] == pytest.approx(235)
    assert currency_report["cash_balance"] == pytest.approx(235)
    assert currency_report["realized_profit_loss"] == pytest.approx(35)
    assert currency_report["profit_loss"] == pytest.approx(35)
    assert currency_report["unrealized_return_percentage"] is None
    assert currency_report["cumulative_return_percentage"] == pytest.approx(17.5)


def test_cash_balance_includes_trade_flows_and_is_added_to_portfolio_value():
    portfolio = Portfolio()
    portfolio.record_cash("OPENING_CASH", 5000, "USD")
    portfolio.record_opening_balance("AAPL", "US", 10, 100, current_price=130)
    portfolio.record_buy("AAPL", "US", 5, 120, fees=2)
    portfolio.record_sell("AAPL", "US", 5, 130, fees=1)

    summary = portfolio.report()["currencies"]["USD"]
    assert summary["cash_balance"] == pytest.approx(5047)
    assert summary["total_value"] == pytest.approx(6347)
    assert summary["realized_profit_loss"] == pytest.approx(115)
    assert summary["unrealized_profit_loss"] == pytest.approx(232)
    assert summary["profit_loss"] == pytest.approx(347)
    assert summary["net_contributions"] == pytest.approx(6000)
    assert summary["cumulative_return_percentage"] == pytest.approx(347 / 6000 * 100)


def test_cash_deposits_and_withdrawals_are_ordered_ledger_events():
    portfolio = Portfolio()
    portfolio.record_cash("OPENING_CASH", 1000, "USD")
    portfolio.record_cash("CASH_DEPOSIT", 250, "USD")
    portfolio.record_cash("CASH_WITHDRAWAL", 100, "USD")

    assert portfolio._cash_balances()["USD"] == pytest.approx(1150)
    assert portfolio.report()["currencies"]["USD"]["net_contributions"] == pytest.approx(1150)
    assert portfolio.report()["currencies"]["USD"]["cumulative_return_percentage"] == pytest.approx(0)
    with pytest.raises(ValueError, match="chronological order"):
        portfolio.record_cash(
            "CASH_DEPOSIT", 10, "USD", executed_at=datetime(2000, 1, 1, tzinfo=timezone.utc)
        )


def test_cash_reconciliation_matches_actual_balance_and_marks_history_complete():
    portfolio = Portfolio()
    portfolio.record_cash("OPENING_CASH", 1000, "USD")
    portfolio.record_cash("CASH_WITHDRAWAL", 100, "USD")

    adjustment = portfolio.reconcile_cash("USD", 1200)

    assert adjustment == pytest.approx(300)
    assert portfolio._cash_balances()["USD"] == pytest.approx(1200)
    assert portfolio.cash_history_complete is True
    assert portfolio.transactions[-1].side == "CASH_RECONCILIATION"
