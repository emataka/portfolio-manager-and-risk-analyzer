import json
import math
import numbers
import os
import tempfile
from pathlib import Path

from core.models.asset import Asset
from core.models.cash_transaction import CashTransaction
from core.models.portfolio import Portfolio
from core.models.transaction import Transaction


SCHEMA_VERSION = 4
_ASSET_FIELDS_V1 = {"ticker", "quantity", "buy_price", "current_price", "market"}
_ASSET_FIELDS = _ASSET_FIELDS_V1 | {"currency"}
_TRANSACTION_FIELDS = {
    "ticker", "market", "side", "quantity", "price", "fees", "currency", "executed_at"
}


def save_portfolio(portfolio, path, *, overwrite=False):
    """Save portfolio holdings as versioned UTF-8 JSON using an atomic file replace."""
    if not isinstance(portfolio, Portfolio):
        raise TypeError("portfolio must be a Portfolio instance.")
    if not isinstance(portfolio.cash_history_complete, bool):
        raise ValueError("cash_history_complete must be a boolean.")
    if not portfolio.cash_history_complete and any(
        isinstance(transaction, CashTransaction)
        and transaction.side == "CASH_RECONCILIATION"
        for transaction in portfolio.transactions
    ):
        raise ValueError("Cash history metadata conflicts with a reconciliation event.")

    replayed = replay_transactions(
        [transaction.to_record() for transaction in portfolio.transactions]
    )
    _validate_position_snapshot(replayed, portfolio.assets)

    destination = Path(path)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing portfolio file: {destination}")

    document = {
        "schema_version": SCHEMA_VERSION,
        "assets": [_serialize_asset(asset) for asset in portfolio.assets],
        "transactions": [transaction.to_record() for transaction in portfolio.transactions],
        "cash_history_complete": portfolio.cash_history_complete,
    }
    contents = json.dumps(document, ensure_ascii=False, indent=2, allow_nan=False) + "\n"

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)
            temporary_file.write(contents)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())
        os.replace(temporary_path, destination)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def load_portfolio(path):
    """Load and validate a versioned portfolio JSON file."""
    source = Path(path)
    try:
        with source.open("r", encoding="utf-8") as portfolio_file:
            document = json.load(portfolio_file)
    except json.JSONDecodeError as error:
        raise ValueError(f"Portfolio file contains invalid JSON: {source}") from error

    if not isinstance(document, dict):
        raise ValueError("Portfolio document must be a JSON object.")
    schema_version = document.get("schema_version")
    if schema_version not in {1, 2, 3, SCHEMA_VERSION}:
        raise ValueError(
            f"Unsupported portfolio schema version: {schema_version!r}"
        )
    assets = document.get("assets")
    if not isinstance(assets, list):
        raise ValueError("Portfolio document must contain an assets list.")

    snapshots = [
        _deserialize_asset(record, index, schema_version)
        for index, record in enumerate(assets)
    ]

    if schema_version < 3:
        portfolio = Portfolio()
        if schema_version == 1:
            portfolio.migration_warnings.append(
                "Currency was inferred from market (US=USD, IR=IRR). "
                "Verify legacy purchase-price units, especially Iranian holdings, before using P/L."
            )
        portfolio.migration_warnings.append(
            "This legacy snapshot had no transaction history. Each holding was imported as "
            "an opening balance at its saved buy price; earlier realized P/L is unavailable."
        )
        for asset in snapshots:
            try:
                portfolio.add_asset(asset)
            except ValueError as error:
                raise ValueError(f"Invalid asset {asset.ticker!r}: {error}") from error
        portfolio.cash_history_complete = False
        portfolio.migration_warnings.append(_cash_history_warning())
        return portfolio

    transactions = document.get("transactions")
    if not isinstance(transactions, list):
        raise ValueError("Portfolio document must contain a transactions list.")
    portfolio = replay_transactions(transactions)
    _validate_position_snapshot(portfolio, snapshots)
    if schema_version == 3:
        portfolio.cash_history_complete = False
    else:
        cash_history_complete = document.get("cash_history_complete")
        if not isinstance(cash_history_complete, bool):
            raise ValueError("Portfolio document must contain a boolean cash_history_complete field.")
        if not cash_history_complete and any(
            isinstance(transaction, CashTransaction)
            and transaction.side == "CASH_RECONCILIATION"
            for transaction in portfolio.transactions
        ):
            raise ValueError("Cash history metadata conflicts with a reconciliation event.")
        portfolio.cash_history_complete = cash_history_complete
    if not portfolio.cash_history_complete:
        portfolio.migration_warnings.append(_cash_history_warning())
    return portfolio


def _cash_history_warning():
    return (
        "Cash history is incomplete. Reported cash includes only recorded cash events and "
        "buy/sell flows; reconcile it with the current broker balance before relying on total value."
    )


def _deserialize_asset(record, index, schema_version):
    expected_fields = _ASSET_FIELDS_V1 if schema_version == 1 else _ASSET_FIELDS
    if not isinstance(record, dict) or set(record) != expected_fields:
        raise ValueError(f"Asset at position {index} has an invalid field set.")
    ticker = record["ticker"]
    market = record["market"]
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError(f"Asset at position {index} must have a non-empty ticker.")
    if not isinstance(market, str):
        raise ValueError(f"Asset at position {index} must have a market string.")
    quantity = _positive_number(record["quantity"], "quantity", index)
    buy_price = _positive_number(record["buy_price"], "buy_price", index)
    current_price = _positive_number(record["current_price"], "current_price", index)
    currency = record.get("currency")
    try:
        return Asset(
            ticker.strip(), quantity, buy_price, market,
            current_price=current_price, currency=currency,
        )
    except (TypeError, ValueError) as error:
        raise ValueError(f"Invalid asset at position {index}: {error}") from error


def replay_transactions(records):
    """Rebuild a portfolio from its ordered, serialized ledger events."""
    portfolio = Portfolio()
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            raise ValueError(f"Transaction at position {index} must be an object.")
        try:
            if record.get("type") == "cash":
                if set(record) != {"type", "side", "amount", "currency", "executed_at"}:
                    raise ValueError("Cash transaction has an invalid field set.")
                transaction = CashTransaction(
                    record["side"], record["amount"], record["currency"],
                    executed_at=record["executed_at"],
                )
                portfolio._append_cash_transaction(transaction)
                continue
            if set(record) != _TRANSACTION_FIELDS:
                raise ValueError("Transaction has an invalid field set.")
            transaction = Transaction(**record)
            if transaction.side == "OPENING_BALANCE":
                portfolio.record_opening_balance(
                    transaction.ticker,
                    transaction.market,
                    transaction.quantity,
                    transaction.price,
                    fees=transaction.fees,
                    executed_at=transaction.executed_at,
                )
            elif transaction.side == "BUY":
                portfolio.record_buy(
                    transaction.ticker,
                    transaction.market,
                    transaction.quantity,
                    transaction.price,
                    fees=transaction.fees,
                    executed_at=transaction.executed_at,
                )
            else:
                portfolio.record_sell(
                    transaction.ticker,
                    transaction.market,
                    transaction.quantity,
                    transaction.price,
                    fees=transaction.fees,
                    executed_at=transaction.executed_at,
                )
        except (TypeError, ValueError) as error:
            raise ValueError(f"Invalid transaction at position {index}: {error}") from error
    return portfolio


def _validate_position_snapshot(portfolio, snapshots):
    positions = {asset.ticker: asset for asset in portfolio.assets}
    saved_positions = {asset.ticker: asset for asset in snapshots}
    if len(saved_positions) != len(snapshots) or set(positions) != set(saved_positions):
        raise ValueError("Saved holdings do not match the positions reconstructed from transactions.")

    for ticker, position in positions.items():
        saved = saved_positions[ticker]
        if (
            position.market != saved.market
            or position.currency != saved.currency
            or not math.isclose(position.quantity, saved.quantity, rel_tol=1e-9, abs_tol=1e-9)
            or not math.isclose(position.buy_price, saved.buy_price, rel_tol=1e-9, abs_tol=1e-9)
        ):
            raise ValueError(f"Saved holding {ticker!r} does not match its transaction history.")
        position.current_price = saved.current_price


def _serialize_asset(asset):
    ticker = getattr(asset, "ticker", None)
    market = getattr(asset, "market", None)
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("Portfolio assets must have a non-empty ticker.")
    if not isinstance(market, str):
        raise ValueError(f"Asset {ticker!r} must have a market string.")
    return {
        "ticker": ticker,
        "quantity": _positive_number(asset.quantity, "quantity", ticker),
        "buy_price": _positive_number(asset.buy_price, "buy_price", ticker),
        "current_price": _positive_number(asset.current_price, "current_price", ticker),
        "market": market,
        "currency": asset.currency,
    }


def _positive_number(value, field, asset_identifier):
    if isinstance(value, bool) or not isinstance(value, numbers.Real):
        raise ValueError(f"Asset {asset_identifier!r} field {field!r} must be numeric.")
    numeric_value = float(value)
    if not math.isfinite(numeric_value) or numeric_value <= 0:
        raise ValueError(
            f"Asset {asset_identifier!r} field {field!r} must be finite and greater than zero."
        )
    return numeric_value
