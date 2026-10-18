from core.data.data_service import MarketDataService
from core.models.asset import Asset
from core.models.portfolio import Portfolio


def print_report(report, stale_tickers=None):
    stale_tickers = set(stale_tickers or ())
    print("\n--- Portfolio Report (amounts grouped by currency; no FX conversion) ---\n")
    if not report.get("cash_history_complete", True):
        print(
            "WARNING: cash history is incomplete. Reconcile cash with the current "
            "broker balance before relying on total value.\n"
        )
    
    for asset_info in report["assets"]:
        print(
            f"{asset_info['ticker']} [{asset_info['market']}/{asset_info['currency']}] | "
            f"Qty: {asset_info['quantity']:g} | "
            f"Buy: {asset_info['buy_price']} | "
            f"Current: {asset_info['current_price']:.2f} | "
            f"Value: {asset_info['value']:.2f} | "
            f"Unrealized P/L: {asset_info['profit_loss']:.2f} {asset_info['currency']} | "
            f"Currency weight: {asset_info['currency_weight']:.2f}%"
            f"{' | PRICE NOT UPDATED (last saved price)' if asset_info['ticker'] in stale_tickers else ''}"
        )

    print("\n--- Currency summaries (native price units) ---")
    if not report["currencies"]:
        print("No holdings.")
    for currency, totals in report["currencies"].items():
        print(f"{currency} | TOTAL VALUE: {totals['total_value']:.2f}")
        print(f"{currency} | SECURITIES VALUE: {totals['securities_value']:.2f}")
        print(f"{currency} | CASH BALANCE: {totals['cash_balance']:.2f}")
        if totals["cash_balance"] < 0:
            print(
                f"{currency} | WARNING: negative cash; initial funding may be missing "
                "or recorded spending exceeds cash."
            )
        print(f"{currency} | SECURITIES COST BASIS: {totals['cost_basis']:.2f}")
        print(f"{currency} | REALIZED P/L: {totals['realized_profit_loss']:.2f}")
        print(f"{currency} | UNREALIZED P/L: {totals['unrealized_profit_loss']:.2f}")
        print(f"{currency} | TOTAL P/L: {totals['profit_loss']:.2f}")
        unrealized_return = totals["unrealized_return_percentage"]
        return_text = "N/A" if unrealized_return is None else f"{unrealized_return:.2f}%"
        print(f"{currency} | UNREALIZED RETURN: {return_text}")
        cumulative_return = totals["cumulative_return_percentage"]
        cumulative_return_text = "N/A" if cumulative_return is None else f"{cumulative_return:.2f}%"
        print(f"{currency} | CUMULATIVE RETURN ON NET CONTRIBUTIONS: {cumulative_return_text}")

def print_risk_check(risk_data):
        print("\n--- Risk Analysis ---\n")
        
        for asset_risk in risk_data:
            print(
                f"{asset_risk['ticker']} [{asset_risk['market']}/{asset_risk['currency']}] | "
                f"currency weight: {asset_risk['currency_weight']:.2f}% | "
                f"{asset_risk['level']}"
            )

def main(portfolio=None):
    if portfolio is None:
        print("نمونهٔ آزمایشی: مقادیر خرید فرضی‌اند و نباید به‌عنوان عملکرد واقعی تفسیر شوند.")
        portfolio = Portfolio()
        a1 = Asset("AAPL", 10, 100, "US")
        a2 = Asset("TSLA", 5, 200, "US")
        a3 = Asset("NVDA", 20, 150, "US")
        a4 = Asset("وبملت", 100, 5000, "IR")
        for asset in [a1, a2, a3, a4]:
            try:
                portfolio.add_asset(asset)
            except ValueError as e:
                print(e)

    market_data_service = MarketDataService()
    
    print("=== BEFORE UPDATE ===")
    print_report(portfolio.report())
    
    result = market_data_service.update_portfolio_prices(portfolio)
    print(f"Updated: {result['updated']}")
    print(f"Failed: {result['failed']}")
    if result["failures"]:
        print("Prices below could not be refreshed; their last saved prices remain in the report:")
        for failure in result["failures"]:
            print(f"- {failure['ticker']} [{failure['market']}]: {failure['error']}")
    
    print("\n=== AFTER UPDATE ===")
    stale_tickers = {failure["ticker"] for failure in result["failures"]}
    print_report(portfolio.report(), stale_tickers=stale_tickers)
    
    print_risk_check(portfolio.risk_check())
    return portfolio

if __name__ == "__main__":
    main()
