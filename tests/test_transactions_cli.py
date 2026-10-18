from core.models.portfolio import Portfolio
from cli.transactions_cli import manage_transactions


def test_transaction_menu_records_buy_with_market_currency(monkeypatch):
    answers = iter(["2", "AAPL", "1", "2", "100", "1", "", "6"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    portfolio = Portfolio()

    result = manage_transactions(portfolio)

    assert result is portfolio
    assert len(portfolio.transactions) == 1
    transaction = portfolio.transactions[0]
    assert transaction.side == "BUY"
    assert transaction.ticker == "AAPL"
    assert transaction.currency == "USD"
    assert transaction.quantity == 2
    assert transaction.price == 100
    assert transaction.fees == 1


def test_transaction_menu_records_opening_cash(monkeypatch):
    answers = iter(["5", "1", "1", "2500", "", "6"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    portfolio = Portfolio()

    manage_transactions(portfolio)

    assert portfolio._cash_balances() == {"USD": 2500}
    assert portfolio.report()["currencies"]["USD"]["total_value"] == 2500


def test_transaction_menu_reconciles_cash_balance(monkeypatch):
    answers = iter(["5", "4", "1", "900", "", "6"])
    monkeypatch.setattr("builtins.input", lambda _prompt="": next(answers))
    portfolio = Portfolio()
    portfolio.record_cash("OPENING_CASH", 1000, "USD")

    manage_transactions(portfolio)

    assert portfolio._cash_balances()["USD"] == 900
    assert portfolio.cash_history_complete is True
