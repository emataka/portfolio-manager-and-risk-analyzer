"""Validated, preview-first CSV import/export for portfolio transaction ledgers."""

import csv
from copy import deepcopy
from dataclasses import dataclass
import hashlib
import io
import json
import os
from pathlib import Path
import tempfile

from core.models.cash_transaction import CashTransaction
from core.models.portfolio import Portfolio
from core.models.transaction import Transaction


CSV_FIELDS = (
    "record_type",
    "side",
    "ticker",
    "market",
    "quantity",
    "price",
    "fees",
    "amount",
    "currency",
    "executed_at",
)
MAX_IMPORT_BYTES = 5 * 1024 * 1024
MAX_IMPORT_ROWS = 10000


@dataclass(frozen=True)
class CSVImportPreview:
    row_count: int
    events: tuple
    duplicate_rows: tuple
    errors: tuple
    base_fingerprint: str

    @property
    def importable_count(self):
        return len(self.events)


def preview_transactions_csv(portfolio, path):
    """Parse and validate a CSV without mutating the supplied portfolio.

    Exact duplicate events are excluded and reported. Any malformed row or
    ledger-order/accounting error blocks the whole import.
    """
    if not isinstance(portfolio, Portfolio):
        raise TypeError("portfolio must be a Portfolio instance.")

    source = Path(path)
    if source.stat().st_size > MAX_IMPORT_BYTES:
        raise ValueError(f"CSV file exceeds the {MAX_IMPORT_BYTES // (1024 * 1024)} MB limit.")
    with source.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if tuple(reader.fieldnames or ()) != CSV_FIELDS:
            raise ValueError(
                "CSV headers do not match the transaction template. "
                f"Expected: {', '.join(CSV_FIELDS)}"
            )
        parsed_events = []
        errors = []
        duplicate_rows = []
        existing_fingerprints = {_event_fingerprint(event) for event in portfolio.transactions}
        seen_fingerprints = set()
        row_count = 0

        for row_number, row in enumerate(reader, start=2):
            row_count += 1
            if row_count > MAX_IMPORT_ROWS:
                errors.append(f"CSV exceeds the {MAX_IMPORT_ROWS} data-row limit.")
                break
            if None in row or any(value is None for value in row.values()):
                errors.append(f"Row {row_number}: row has extra or missing CSV columns.")
                continue
            normalized = {key: (value or "").strip() for key, value in row.items()}
            try:
                event = _parse_event(normalized)
            except (TypeError, ValueError) as error:
                errors.append(f"Row {row_number}: {error}")
                continue

            fingerprint = _event_fingerprint(event)
            if fingerprint in existing_fingerprints or fingerprint in seen_fingerprints:
                duplicate_rows.append(row_number)
                continue
            seen_fingerprints.add(fingerprint)
            parsed_events.append((row_number, event))

    base_fingerprint = _portfolio_fingerprint(portfolio)
    if errors:
        return CSVImportPreview(
            row_count, (), tuple(duplicate_rows), tuple(errors), base_fingerprint
        )

    candidate = deepcopy(portfolio)
    for row_number, event in parsed_events:
        try:
            _apply_event(candidate, event)
        except (TypeError, ValueError) as error:
            errors.append(f"Row {row_number}: {error}")
            break

    return CSVImportPreview(
        row_count,
        tuple(parsed_events) if not errors else (),
        tuple(duplicate_rows),
        tuple(errors),
        base_fingerprint,
    )


def apply_transactions_csv_import(portfolio, preview):
    """Apply a valid preview atomically, if the portfolio has not changed."""
    if not isinstance(portfolio, Portfolio):
        raise TypeError("portfolio must be a Portfolio instance.")
    if not isinstance(preview, CSVImportPreview):
        raise TypeError("preview must be a CSVImportPreview instance.")
    if preview.errors:
        raise ValueError("CSV preview contains errors; no rows were imported.")
    if _portfolio_fingerprint(portfolio) != preview.base_fingerprint:
        raise ValueError("Portfolio changed after preview. Create a new CSV preview before importing.")
    if not preview.events:
        return 0

    candidate = deepcopy(portfolio)
    for _, event in preview.events:
        _apply_event(candidate, event)

    portfolio.assets = candidate.assets
    portfolio.transactions = candidate.transactions
    portfolio.realized_profit_loss_by_currency = candidate.realized_profit_loss_by_currency
    portfolio.migration_warnings = candidate.migration_warnings
    portfolio.cash_history_complete = candidate.cash_history_complete
    return len(preview.events)


def export_transactions_csv(portfolio, path, *, overwrite=False):
    """Write the ledger atomically as UTF-8 with a BOM for spreadsheet apps."""
    if not isinstance(portfolio, Portfolio):
        raise TypeError("portfolio must be a Portfolio instance.")
    destination = Path(path)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing CSV file: {destination}")

    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\r\n")
    writer.writeheader()
    for event in portfolio.transactions:
        writer.writerow(_event_to_csv_row(event))
    contents = buffer.getvalue().encode("utf-8-sig")

    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
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


def write_transactions_csv_template(path, *, overwrite=False):
    """Write a template with one trade and one cash example."""
    destination = Path(path)
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing CSV file: {destination}")
    rows = [
        {
            "record_type": "TRADE", "side": "OPENING_BALANCE", "ticker": "نماد",
            "market": "IR", "quantity": "10", "price": "1000", "fees": "0",
            "amount": "", "currency": "IRR", "executed_at": "2025-01-01T09:00:00+03:30",
        },
        {
            "record_type": "CASH", "side": "OPENING_CASH", "ticker": "",
            "market": "", "quantity": "", "price": "", "fees": "",
            "amount": "1000000", "currency": "IRR", "executed_at": "2025-01-01T09:00:00+03:30",
        },
    ]
    _write_rows_atomically(destination, rows, overwrite=overwrite)


def _write_rows_atomically(destination, rows, *, overwrite):
    if destination.exists() and not overwrite:
        raise FileExistsError(f"Refusing to overwrite existing CSV file: {destination}")
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=CSV_FIELDS, lineterminator="\r\n")
    writer.writeheader()
    writer.writerows(rows)
    contents = buffer.getvalue().encode("utf-8-sig")
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
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


def _parse_event(row):
    record_type = row["record_type"].upper()
    executed_at = _required(row, "executed_at")
    if record_type == "TRADE":
        if row["amount"]:
            raise ValueError("amount must be empty for TRADE rows.")
        return Transaction(
            ticker=_required(row, "ticker"),
            market=_required(row, "market"),
            side=_required(row, "side"),
            quantity=_number(row, "quantity"),
            price=_number(row, "price"),
            fees=_number(row, "fees", default="0", allow_zero=True),
            currency=_required(row, "currency"),
            executed_at=executed_at,
        )
    if record_type == "CASH":
        if any(row[field] for field in ("ticker", "market", "quantity", "price", "fees")):
            raise ValueError("ticker, market, quantity, price, and fees must be empty for CASH rows.")
        side = _required(row, "side").upper()
        return CashTransaction(
            side,
            _number(
                row,
                "amount",
                allow_zero=side == "CASH_RECONCILIATION",
                allow_negative=side == "CASH_RECONCILIATION",
            ),
            _required(row, "currency"),
            executed_at=executed_at,
        )
    raise ValueError("record_type must be TRADE or CASH.")


def _apply_event(portfolio, event):
    if isinstance(event, Transaction):
        if event.side == "OPENING_BALANCE":
            portfolio.record_opening_balance(
                event.ticker, event.market, event.quantity, event.price,
                fees=event.fees, executed_at=event.executed_at,
            )
        elif event.side == "BUY":
            portfolio.record_buy(
                event.ticker, event.market, event.quantity, event.price,
                fees=event.fees, executed_at=event.executed_at,
            )
        else:
            portfolio.record_sell(
                event.ticker, event.market, event.quantity, event.price,
                fees=event.fees, executed_at=event.executed_at,
            )
        return

    if event.side == "CASH_RECONCILIATION":
        currency = event.currency
        current_balance = portfolio._cash_balances().get(currency, 0.0)
        portfolio.reconcile_cash(
            currency,
            current_balance + event.amount,
            executed_at=event.executed_at,
        )
    else:
        portfolio.record_cash(
            event.side,
            event.amount,
            event.currency,
            executed_at=event.executed_at,
        )


def _event_to_csv_row(event):
    if isinstance(event, CashTransaction):
        return {
            "record_type": "CASH", "side": event.side, "ticker": "", "market": "",
            "quantity": "", "price": "", "fees": "", "amount": _format_number(event.amount),
            "currency": event.currency, "executed_at": event.executed_at.isoformat(),
        }
    return {
        "record_type": "TRADE", "side": event.side, "ticker": event.ticker,
        "market": event.market, "quantity": _format_number(event.quantity),
        "price": _format_number(event.price), "fees": _format_number(event.fees),
        "amount": "", "currency": event.currency, "executed_at": event.executed_at.isoformat(),
    }


def _event_fingerprint(event):
    canonical = json.dumps(event.to_record(), sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _portfolio_fingerprint(portfolio):
    canonical = json.dumps(
        [event.to_record() for event in portfolio.transactions],
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _required(row, field):
    value = row[field]
    if not value:
        raise ValueError(f"{field} is required.")
    return value


def _number(row, field, *, default=None, allow_zero=False, allow_negative=False):
    value = row[field] or default
    if value is None:
        raise ValueError(f"{field} is required.")
    try:
        number = float(value)
    except ValueError as error:
        raise ValueError(f"{field} must be a number using a dot as decimal separator.") from error
    if (number < 0 and not allow_negative) or (number == 0 and not allow_zero):
        raise ValueError(f"{field} must be {'non-negative' if allow_zero else 'greater than zero'}.")
    return number


def _format_number(value):
    return repr(float(value))
