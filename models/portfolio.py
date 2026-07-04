from models.asset import Asset

class Portfolio:
    def __init__(self):
        self.assets = []
    
    def add_asset(self, asset: Asset):
        for a in self.assets:
            if a.ticker == asset.ticker:
                raise ValueError("Asset already exists.")
        self.assets.append(asset)
    
    def remove_asset(self, ticker: str):
        for asset in self.assets:
            if asset.ticker == ticker.upper():
                self.assets.remove(asset)
                return
        raise ValueError("Asset not found")

    def calculate_cost_basis(self):
        total = 0
        for asset in self.assets:
            total += asset.quantity * asset.buy_price
        return total
    
    def calculate_profit_loss(self):
        return self.calculate_total_value() - self.calculate_cost_basis()
    
    def calculate_return_percentage(self):
        cost = self.calculate_cost_basis()
        if cost == 0:
            return 0
        return (self.calculate_profit_loss() / cost) * 100
    
    def calculate_total_value(self):
        total = 0
        for asset in self.assets:
            total += asset.market_value()
        return total
    
    def risk_check(self):
        total_value = self.calculate_total_value()
        
        print("\n--- Risk Analysis ---\n")
        
        for asset in self.assets:
            value = asset.market_value()
            weight = (value / total_value) * 100 if total_value > 0 else 0
        
            if weight > 70:
                print(f"HIGH RISK: {asset.ticker} = {weight:.2f}%")
            elif weight > 50:
                print(f"WARNING: {asset.ticker} = {weight:.2f}%")
            else:
                print(f"OK: {asset.ticker} = {weight:.2f}%")
    
    def report(self):
        print("\n--- Portfolio Report ---\n")
        
        total_value = self.calculate_total_value()
        
        for asset in self.assets:
            value = asset.market_value()
            weight = (value / total_value) * 100 if total_value > 0 else 0
            
            print(
                f"{asset.ticker} | "
                f"Qty: {asset.quantity} | "
                f"Buy: {asset.buy_price} | "
                f"Current: {asset.current_price:.2f} | "
                f"Value: {value:.2f} | "
                f"P/L: {asset.profit_loss():.2f} | "
                f"Weight: {weight:.2f}%"
            )
        
        print("\n------------------------")
        print(f"TOTAL VALUE: {total_value:.2f}")
        print(f"COST BASIS: {self.calculate_cost_basis():.2f}")
        print(f"PROFIT/LOSS: {self.calculate_profit_loss():.2f}")
        print(f"RETURN: {self.calculate_return_percentage():.2f}")
