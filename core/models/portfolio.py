import math
import numbers

from .asset import Asset
from .cash_transaction import CashTransaction
from .transaction import Transaction


class Portfolio:
    HIGH_RISK_THRESHOLD = 70
    WARNING_THRESHOLD = 50
    
    def __init__(self):
        self.assets = []
        self.transactions = []
        self.realized_profit_loss_by_currency = {}
        self.migration_warnings = []
        self.cash_history_complete = True
    
    def add_asset(self, asset: Asset):
        transaction = Transaction(
            asset.ticker,
            asset.market,
            "OPENING_BALANCE",
            asset.quantity,
            asset.buy_price,
            currency=asset.currency,
        )
        self._validate_transaction_order(transaction)
        self._add_asset_position(asset)
        self.transactions.append(transaction)

    def _add_asset_position(self, asset):
        for a in self.assets:
            if a.ticker == asset.ticker:
                raise ValueError("Asset already exists.")
        self.assets.append(asset)

    def record_opening_balance(
        self,
        ticker,
        market,
        quantity,
        price,
        *,
        fees=0,
        current_price=None,
        executed_at=None,
    ):
        transaction = Transaction(
            ticker,
            market,
            "OPENING_BALANCE",
            quantity,
            price,
            fees=fees,
            executed_at=executed_at,
        )
        self._validate_transaction_order(transaction)
        effective_cost = transaction.price + transaction.fees / transaction.quantity
        asset = Asset(
            transaction.ticker,
            transaction.quantity,
            effective_cost,
            transaction.market,
            current_price=transaction.price if current_price is None else current_price,
            currency=transaction.currency,
        )
        self._add_asset_position(asset)
        self.transactions.append(transaction)
        return asset

    def record_buy(
        self, ticker, market, quantity, price, *, fees=0, executed_at=None
    ):
        transaction = Transaction(
            ticker, market, "BUY", quantity, price, fees=fees, executed_at=executed_at
        )
        self._validate_transaction_order(transaction)
        asset = next((item for item in self.assets if item.ticker == transaction.ticker), None)
        if asset is None:
            effective_cost = transaction.price + transaction.fees / transaction.quantity
            asset = Asset(
                transaction.ticker,
                transaction.quantity,
                effective_cost,
                transaction.market,
                current_price=transaction.price,
                currency=transaction.currency,
            )
            self._add_asset_position(asset)
        else:
            self._validate_asset_matches_transaction(asset, transaction)
            old_quantity = asset.quantity
            new_quantity = old_quantity + transaction.quantity
            total_cost = (
                old_quantity * asset.buy_price
                + transaction.quantity * transaction.price
                + transaction.fees
            )
            asset.quantity = new_quantity
            asset.buy_price = total_cost / new_quantity
        self.transactions.append(transaction)
        return asset

    def record_sell(
        self, ticker, market, quantity, price, *, fees=0, executed_at=None
    ):
        transaction = Transaction(
            ticker, market, "SELL", quantity, price, fees=fees, executed_at=executed_at
        )
        self._validate_transaction_order(transaction)
        asset = next((item for item in self.assets if item.ticker == transaction.ticker), None)
        if asset is None:
            raise ValueError(f"Cannot sell {transaction.ticker}: no position exists.")
        self._validate_asset_matches_transaction(asset, transaction)
        if transaction.quantity > asset.quantity:
            raise ValueError(
                f"Cannot sell {transaction.quantity}; only {asset.quantity} shares are held."
            )

        quantity_sold = min(transaction.quantity, asset.quantity)
        realized = quantity_sold * (transaction.price - asset.buy_price) - transaction.fees
        currency = transaction.currency
        self.realized_profit_loss_by_currency[currency] = (
            self.realized_profit_loss_by_currency.get(currency, 0.0) + realized
        )
        remaining = asset.quantity - quantity_sold
        if math.isclose(remaining, 0.0, abs_tol=1e-12):
            self.assets.remove(asset)
        else:
            asset.quantity = remaining
        self.transactions.append(transaction)
        return realized

    def _validate_transaction_order(self, transaction):
        if self.transactions and transaction.executed_at < self.transactions[-1].executed_at:
            raise ValueError("Transactions must be recorded in chronological order.")

    def record_cash(self, side, amount, currency, *, executed_at=None):
        transaction = CashTransaction(side, amount, currency, executed_at=executed_at)
        if transaction.side == "CASH_RECONCILIATION":
            raise ValueError("Use reconcile_cash() to record a verified cash balance.")
        return self._append_cash_transaction(transaction)

    def _append_cash_transaction(self, transaction):
        self._validate_transaction_order(transaction)
        self.transactions.append(transaction)
        if transaction.side == "CASH_RECONCILIATION":
            self.cash_history_complete = True
            self.migration_warnings = [
                warning for warning in self.migration_warnings
                if "cash history" not in warning.lower()
            ]
        return transaction

    def reconcile_cash(self, currency, actual_balance, *, executed_at=None):
        if not isinstance(currency, str) or currency.upper() not in {"USD", "IRR"}:
            raise ValueError("Cash currency must be USD or IRR.")
        if isinstance(actual_balance, bool) or not isinstance(actual_balance, numbers.Real):
            raise ValueError("Cash balance must be numeric.")
        if not math.isfinite(actual_balance) or actual_balance < 0:
            raise ValueError("Cash balance must be finite and cannot be negative.")
        current_balance = self._cash_balances().get(currency.upper(), 0.0)
        difference = float(actual_balance) - current_balance
        transaction = CashTransaction(
            "CASH_RECONCILIATION", difference, currency, executed_at=executed_at
        )
        self._append_cash_transaction(transaction)
        return difference

    def _cash_balances(self):
        balances = {}
        for transaction in self.transactions:
            currency = transaction.currency
            if isinstance(transaction, CashTransaction):
                if transaction.side == "CASH_WITHDRAWAL":
                    flow = -transaction.amount
                else:
                    flow = transaction.amount
                balances[currency] = balances.get(currency, 0.0) + flow
            elif transaction.side == "BUY":
                balances[currency] = balances.get(currency, 0.0) - (
                    transaction.quantity * transaction.price + transaction.fees
                )
            elif transaction.side == "SELL":
                balances[currency] = balances.get(currency, 0.0) + (
                    transaction.quantity * transaction.price - transaction.fees
                )
        return balances

    def _net_contributions_by_currency(self):
        contributions = {}
        for transaction in self.transactions:
            currency = transaction.currency
            if isinstance(transaction, CashTransaction):
                if transaction.side in {"OPENING_CASH", "CASH_DEPOSIT"}:
                    flow = transaction.amount
                elif transaction.side == "CASH_WITHDRAWAL":
                    flow = -transaction.amount
                else:
                    # Reconciliation corrects the historical opening cash estimate.
                    flow = transaction.amount
                contributions[currency] = contributions.get(currency, 0.0) + flow
            elif transaction.side == "OPENING_BALANCE":
                contributions[currency] = contributions.get(currency, 0.0) + (
                    transaction.quantity * transaction.price + transaction.fees
                )
        return contributions

    @staticmethod
    def _validate_asset_matches_transaction(asset, transaction):
        if asset.market != transaction.market or asset.currency != transaction.currency:
            raise ValueError(
                f"Transaction market/currency does not match {transaction.ticker} position."
            )
    
    def remove_asset(self, ticker: str):
        for asset in self.assets:
            if asset.ticker == ticker.upper():
                self.record_sell(
                    asset.ticker,
                    asset.market,
                    asset.quantity,
                    asset.current_price,
                )
                return
        raise ValueError("Asset not found")

    def calculate_cost_basis(self):
        return self._single_currency_totals()["cost_basis"]
    
    def calculate_profit_loss(self):
        return self._single_currency_totals()["profit_loss"]
    
    def calculate_return_percentage(self):
        return self._single_currency_totals()["return_percentage"]
    
    def calculate_total_value(self):
        return self._single_currency_totals()["total_value"]

    def _currency_totals(self):
        net_contributions = self._net_contributions_by_currency()
        totals = {
            currency: {
                "total_value": 0.0,
                "securities_value": 0.0,
                "cost_basis": 0.0,
                "cash_balance": 0.0,
                "net_contributions": 0.0,
            }
            for currency in (
                set(self.realized_profit_loss_by_currency)
                | set(self._cash_balances())
                | set(net_contributions)
            )
        }
        cash_balances = self._cash_balances()
        for currency, balance in cash_balances.items():
            totals.setdefault(
                currency,
                {
                    "total_value": 0.0, "securities_value": 0.0,
                    "cost_basis": 0.0, "cash_balance": 0.0,
                    "net_contributions": 0.0,
                },
            )
            totals[currency]["cash_balance"] = balance
        for asset in self.assets:
            market_totals = totals.setdefault(
                asset.currency,
                {
                    "total_value": 0.0, "securities_value": 0.0,
                    "cost_basis": 0.0, "cash_balance": 0.0,
                    "net_contributions": 0.0,
                },
            )
            market_totals["securities_value"] += asset.market_value()
            market_totals["cost_basis"] += asset.cost_basis()

        for currency_totals in totals.values():
            currency_totals["total_value"] = (
                currency_totals["securities_value"] + currency_totals["cash_balance"]
            )

        for currency, currency_totals in totals.items():
            currency_totals["net_contributions"] = net_contributions.get(currency, 0.0)
            currency_totals["unrealized_profit_loss"] = (
                currency_totals["securities_value"] - currency_totals["cost_basis"]
            )
            currency_totals["realized_profit_loss"] = (
                self.realized_profit_loss_by_currency.get(currency, 0.0)
            )
            currency_totals["profit_loss"] = (
                currency_totals["unrealized_profit_loss"]
                + currency_totals["realized_profit_loss"]
            )
            currency_totals["unrealized_return_percentage"] = (
                currency_totals["unrealized_profit_loss"] / currency_totals["cost_basis"] * 100
                if currency_totals["cost_basis"]
                else None
            )
            currency_totals["return_percentage"] = currency_totals[
                "unrealized_return_percentage"
            ]
            currency_totals["cumulative_return_percentage"] = (
                currency_totals["profit_loss"] / currency_totals["net_contributions"] * 100
                if self.cash_history_complete and currency_totals["net_contributions"] > 0
                else None
            )
        return totals

    def _single_currency_totals(self):
        totals = self._currency_totals()
        if len(totals) > 1:
            currencies = ", ".join(sorted(totals))
            raise ValueError(
                "Cannot combine amounts across currencies "
                f"({currencies}) without currency conversion. Use report()['currencies']."
            )
        if not totals:
            return {
                "total_value": 0.0,
                "cost_basis": 0.0,
                "profit_loss": 0.0,
                "return_percentage": 0.0,
            }
        return next(iter(totals.values()))
    
    def risk_check(self):
        currency_totals = self._currency_totals()
        asset_risk = []
        for asset in self.assets:
            value = asset.market_value()
            total_value = currency_totals[asset.currency]["total_value"]
            weight = (value / total_value) * 100 if total_value > 0 else 0
            
            if weight > self.HIGH_RISK_THRESHOLD:
                level = "high"
            elif weight > self.WARNING_THRESHOLD:
                level = "warning"
            else:
                level = "ok"

            asset_status = {
                "ticker": asset.ticker,
                "market": asset.market,
                "currency": asset.currency,
                "currency_weight": weight,
                "level": level,
            }
            asset_risk.append(asset_status)
        return asset_risk
    
    def report(self):
        currency_totals = self._currency_totals()
        asset_data = []
        for asset in self.assets:
            value = asset.market_value()
            currency_value = currency_totals[asset.currency]["total_value"]
            weight = (value / currency_value) * 100 if currency_value > 0 else 0
            
            asset_info = {
                "ticker": asset.ticker,
                "market": asset.market,
                "currency": asset.currency,
                "quantity": asset.quantity,
                "buy_price": asset.buy_price,
                "current_price": asset.current_price,
                "value": value,
                "profit_loss": asset.profit_loss(),
                "weight": weight,
                "currency_weight": weight,
            }
            asset_data.append(asset_info)

        # Keep scalar summary fields for single-currency portfolios. For mixed
        # currencies, exposing a scalar would silently add unlike units.
        summary = next(iter(currency_totals.values())) if len(currency_totals) == 1 else None
        return {
            "assets": asset_data,
            "currencies": currency_totals,
            "cash_history_complete": self.cash_history_complete,
            "total_value": summary["total_value"] if summary else (0.0 if not currency_totals else None),
            "cost_basis": summary["cost_basis"] if summary else (0.0 if not currency_totals else None),
            "profit_loss": summary["profit_loss"] if summary else (0.0 if not currency_totals else None),
            "return_percentage": summary["return_percentage"] if summary else (0.0 if not currency_totals else None),
        }
