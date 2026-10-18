from core.models.asset import Asset
from core.models.portfolio import Portfolio
from cli.main import print_report


def test_report_marks_failed_price_as_stale_and_uses_market_totals(capsys):
    portfolio = Portfolio()
    portfolio.add_asset(Asset("AAPL", 1, 100, "US", current_price=123))
    portfolio.add_asset(Asset("وبملت", 1, 5000, "IR", current_price=5100))

    print_report(portfolio.report(), stale_tickers={"AAPL"})

    output = capsys.readouterr().out
    assert "AAPL [US/USD]" in output
    assert "PRICE NOT UPDATED (last saved price)" in output
    assert "TOTAL VALUE: 123.00" in output
    assert "TOTAL VALUE: 5100.00" in output
    assert "no FX conversion" in output
    assert "USD | TOTAL VALUE: 123.00" in output
    assert "IRR | TOTAL VALUE: 5100.00" in output
