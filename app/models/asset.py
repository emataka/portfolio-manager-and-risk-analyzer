class Asset:
    def __init__(self, ticker, quantity, buy_price, current_price=None):
        
        ticker = ticker.upper()
        self.ticker = ticker
        
        if quantity <= 0:
            raise ValueError("Quantity must be greater than zero.")
        
        if buy_price <= 0:
            raise ValueError("Buy price must be greater than zero.")
        
        self.ticker = ticker
        self.quantity = quantity
        self.buy_price = buy_price
        if current_price is None:
            self.current_price = buy_price
        else:
            self.update_price(current_price)
    
    def cost_basis(self):
        return self.quantity * self.buy_price
    
    def __str__(self):
        return f"{self.ticker} | Quantity: {self.quantity} | Buy Price: {self.buy_price}"
    
    def __repr__(self):
        return f"Asset('{self.ticker}', {self.quantity}, {self.buy_price})"
    
    def market_value(self):
        return self.quantity * self.current_price
    
    def profit_loss(self):
        return (self.current_price - self.buy_price) * self.quantity
    
    def update_price(self, price):
        if price <= 0:
            raise ValueError("Price must be greater than 0")
        self.current_price = price
