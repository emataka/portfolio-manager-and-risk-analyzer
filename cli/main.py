from core.data.data_service import MarketDataService
from core.models.asset import Asset
from core.models.portfolio import Portfolio


def print_report(report):
    print("\n--- Portfolio Report ---\n")
    
    for asset_info in report["assets"]:
        print(
            f"{asset_info['ticker']} | "
            f"Qty: {asset_info['quantity']} | "
            f"Buy: {asset_info['buy_price']} | "
            f"Current: {asset_info['current_price']:.2f} | "
            f"Value: {asset_info['value']:.2f} | "
            f"P/L: {asset_info['profit_loss']:.2f} | "
            f"Weight: {asset_info['weight']:.2f}%"
        )
    
    print("\n------------------------")
    print(f"TOTAL VALUE: {report['total_value']:.2f}")
    print(f"COST BASIS: {report['cost_basis']:.2f}")
    print(f"PROFIT/LOSS: {report['profit_loss']:.2f}")
    print(f"RETURN: {report['return_percentage']:.2f}")

def print_risk_check(risk_data):
        print("\n--- Risk Analysis ---\n")
        
        for asset_risk in risk_data:
            print(
                f"{asset_risk['ticker']} | "
                f"{asset_risk['level']}"
            )

def main():
    portfolio = Portfolio()
    market_data_service = MarketDataService()
    
    a1 = Asset("AAPL", 10, 100, "US")
    a2 = Asset("TSLA", 5, 200, "US")
    a3 = Asset("NVDA", 20, 150, "US")
    a4 = Asset("ABC123", 10, 70, "US")
    a5 = Asset("وبملت", 100, 5000, "IR")
    
    for asset in [a1, a2, a3, a4, a5]:
        try:
            portfolio.add_asset(asset)
        except ValueError as e:
            print(e)
    
    print("=== BEFORE UPDATE ===")
    print_report(portfolio.report())
    
    result = market_data_service.update_portfolio_prices(portfolio)
    print(f"Updated: {result['updated']}")
    print(f"Failed: {result['failed']}")
    
    print("\n=== AFTER UPDATE ===")
    print_report(portfolio.report())
    
    print_risk_check(portfolio.risk_check())

if __name__ == "__main__":
    main()
