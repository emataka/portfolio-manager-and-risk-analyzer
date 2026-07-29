from .asset import Asset


class Portfolio:
    HIGH_RISK_THRESHOLD = 70
    WARNING_THRESHOLD = 50
    
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
            total += asset.cost_basis()
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
        
        asset_risk = []
        
        for asset in self.assets:
            value = asset.market_value()
            weight = (value / total_value) * 100 if total_value > 0 else 0
            
            if weight > self.HIGH_RISK_THRESHOLD:
                level = "high"
            elif weight > self.WARNING_THRESHOLD:
                level = "warning"
            else:
                level = "ok"

            asset_status = {
                "ticker": asset.ticker,
                "level": level,
            }
            
            asset_risk.append(asset_status)
        
        return asset_risk
    
    def report(self):
        total_value = self.calculate_total_value()
        
        asset_data = []
        
        for asset in self.assets:
            value = asset.market_value()
            weight = (value / total_value) * 100 if total_value > 0 else 0
            
            asset_info = {
                "ticker": asset.ticker,
                "quantity": asset.quantity,
                "buy_price": asset.buy_price,
                "current_price": asset.current_price,
                "value": value,
                "profit_loss": asset.profit_loss(),
                "weight": weight,
            }
        
            asset_data.append(asset_info)
        
        return {
            "assets":asset_data,
            "total_value": total_value,
            "cost_basis": self.calculate_cost_basis(),
            "profit_loss": self.calculate_profit_loss(),
            "return_percentage": self.calculate_return_percentage(),
        }
