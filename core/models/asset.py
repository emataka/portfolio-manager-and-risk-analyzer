class Asset:
    MARKET_CURRENCIES = {"US": "USD", "IR": "IRR"}

    def __init__(self, ticker, quantity, buy_price, market, current_price=None, currency=None):
        
        self.ticker = ticker.upper()
        self.quantity = quantity
        self.buy_price = buy_price
        self.market = market.upper()
        expected_currency = self.MARKET_CURRENCIES[self.market]
        self.currency = expected_currency if currency is None else currency
        if current_price is None:
            self.current_price = buy_price
        else:
            self.update_price(current_price)
    
    @property
    def quantity(self):
        return self._quantity
    
    @quantity.setter
    def quantity(self, value):
        if value <= 0:
            raise ValueError("Quantity must be greater than zero.")
        self._quantity = value
    
    @property
    def buy_price(self):
        return self._buy_price
    
    @buy_price.setter
    def buy_price(self, value):
        if value <= 0:
            raise ValueError("Buy price must be greater than zero.")
        self._buy_price = value
    
    @property
    def market(self):
        return self._market
    
    @market.setter
    def market(self, value):
        if value not in ["IR", "US"]:
            raise ValueError(f"Market must be 'US' or 'IR'. Got {value}")
        self._market = value

    @property
    def currency(self):
        return self._currency

    @currency.setter
    def currency(self, value):
        if not isinstance(value, str) or len(value) != 3 or not value.isalpha():
            raise ValueError("Currency must be a three-letter code such as USD or IRR.")
        value = value.upper()
        expected_currency = self.MARKET_CURRENCIES[self.market]
        if value != expected_currency:
            raise ValueError(
                f"Market {self.market} quotes prices in {expected_currency}; got {value}."
            )
        self._currency = value
    
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
