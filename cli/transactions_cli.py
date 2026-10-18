import csv
from datetime import datetime, timezone
from pathlib import Path

from core.import_export.transaction_csv import (
    apply_transactions_csv_import,
    export_transactions_csv,
    preview_transactions_csv,
    write_transactions_csv_template,
)
from core.models.asset import Asset
from core.models.cash_transaction import CashTransaction


def manage_transactions(portfolio):
    while True:
        print("\nدفتر معاملات")
        print("1. ثبت موجودی آغازین")
        print("2. ثبت خرید")
        print("3. ثبت فروش")
        print("4. نمایش تاریخچه")
        print("5. ثبت وجه نقد")
        print("6. بازگشت")
        print("7. واردکردن دفتر معاملات از CSV")
        print("8. خروجی گرفتن از دفتر معاملات به CSV")
        print("9. ساخت قالب CSV")
        choice = input("انتخاب شما: ").strip()

        if choice == "1":
            _record_opening_balance(portfolio)
        elif choice == "2":
            _record_buy(portfolio)
        elif choice == "3":
            _record_sell(portfolio)
        elif choice == "4":
            _show_history(portfolio)
        elif choice == "5":
            _record_cash(portfolio)
        elif choice == "6":
            return portfolio
        elif choice == "7":
            _import_transactions_csv(portfolio)
        elif choice == "8":
            _export_transactions_csv(portfolio)
        elif choice == "9":
            _write_transactions_csv_template()


def _import_transactions_csv(portfolio):
    path = input("مسیر فایل CSV: ").strip()
    if not path:
        print("مسیر فایل وارد نشده است.")
        return
    try:
        preview = preview_transactions_csv(portfolio, path)
    except (OSError, UnicodeError, csv.Error, ValueError) as error:
        print(f"پیش‌نمایش انجام نشد: {error}")
        return

    print(f"\nپیش‌نمایش CSV: {preview.row_count} ردیف")
    if preview.errors:
        print("به‌دلیل خطا، هیچ ردیفی قابل ثبت نیست:")
        for error in preview.errors:
            print(f"- {error}")
        return
    if preview.duplicate_rows:
        rows = ", ".join(map(str, preview.duplicate_rows))
        print(
            f"ردیف‌های تکراری شناسایی‌شده وارد نمی‌شوند: {len(preview.duplicate_rows)} "
            f"(ردیف‌های {rows})"
        )
    for row_number, event in preview.events[:10]:
        print(f"ردیف {row_number}: {_describe_csv_event(event)}")
    if preview.importable_count > 10:
        print(f"... و {preview.importable_count - 10} ردیف معتبر دیگر")
    if not preview.importable_count:
        print("رویداد جدیدی برای واردکردن وجود ندارد.")
        return

    confirmation = input(
        f"برای ثبت اتمیک {preview.importable_count} رویداد، عبارت IMPORT را وارد کن: "
    ).strip()
    if confirmation != "IMPORT":
        print("واردکردن لغو شد؛ پرتفوی تغییر نکرد.")
        return
    try:
        imported = apply_transactions_csv_import(portfolio, preview)
    except (TypeError, ValueError) as error:
        print(f"واردکردن انجام نشد؛ پرتفوی تغییر نکرد: {error}")
    else:
        print(f"{imported} رویداد با موفقیت وارد شد.")


def _export_transactions_csv(portfolio):
    path = input("مسیر خروجی (پیش‌فرض: transactions.csv): ").strip() or "transactions.csv"
    overwrite = False
    if Path(path).exists():
        overwrite = input("فایل وجود دارد؛ برای بازنویسی YES را وارد کن: ").strip() == "YES"
        if not overwrite:
            print("خروجی لغو شد؛ فایل موجود تغییر نکرد.")
            return
    try:
        export_transactions_csv(portfolio, path, overwrite=overwrite)
    except (OSError, ValueError) as error:
        print(f"خروجی CSV انجام نشد: {error}")
    else:
        print(f"دفتر معاملات در {path} ذخیره شد.")


def _write_transactions_csv_template():
    path = input("مسیر قالب (پیش‌فرض: transactions-template.csv): ").strip() or "transactions-template.csv"
    overwrite = False
    if Path(path).exists():
        overwrite = input("فایل وجود دارد؛ برای بازنویسی YES را وارد کن: ").strip() == "YES"
        if not overwrite:
            print("ساخت قالب لغو شد؛ فایل موجود تغییر نکرد.")
            return
    try:
        write_transactions_csv_template(path, overwrite=overwrite)
    except (OSError, ValueError) as error:
        print(f"ساخت قالب CSV انجام نشد: {error}")
    else:
        print(f"قالب CSV در {path} ساخته شد. ردیف‌های نمونه را با اطلاعات خودت جایگزین کن.")


def _describe_csv_event(event):
    if isinstance(event, CashTransaction):
        return f"وجه نقد {event.side} | {event.amount:g} {event.currency} | {event.executed_at.isoformat()}"
    return (
        f"{event.side} | {event.ticker} [{event.market}/{event.currency}] | "
        f"{event.quantity:g} × {event.price:g} | fees: {event.fees:g} | "
        f"{event.executed_at.isoformat()}"
    )


def _record_opening_balance(portfolio):
    try:
        ticker = input("نماد: ").strip()
        market = _read_market()
        quantity = _read_number("تعداد: ", allow_zero=False)
        price = _read_number(f"قیمت هر سهم ({Asset.MARKET_CURRENCIES[market]}): ", allow_zero=False)
        fees = _read_number("کارمزد کل (پیش‌فرض ۰): ", allow_zero=True, default=0)
        executed_at = _read_timestamp()
        portfolio.record_opening_balance(
            ticker,
            market,
            quantity,
            price,
            fees=fees,
            executed_at=executed_at,
        )
    except (ValueError, KeyError) as error:
        print(f"ثبت موجودی انجام نشد: {error}")
    else:
        print("موجودی آغازین ثبت شد.")


def _record_buy(portfolio):
    try:
        ticker = input("نماد: ").strip()
        market = _read_market()
        quantity = _read_number("تعداد خرید: ", allow_zero=False)
        price = _read_number(f"قیمت هر سهم ({Asset.MARKET_CURRENCIES[market]}): ", allow_zero=False)
        fees = _read_number("کارمزد کل (پیش‌فرض ۰): ", allow_zero=True, default=0)
        executed_at = _read_timestamp()
        portfolio.record_buy(
            ticker, market, quantity, price, fees=fees, executed_at=executed_at
        )
    except (ValueError, KeyError) as error:
        print(f"ثبت خرید انجام نشد: {error}")
    else:
        print("خرید ثبت شد؛ بهای تمام‌شده با میانگین موزون به‌روزرسانی شد.")


def _record_sell(portfolio):
    try:
        ticker = input("نماد: ").strip()
        market = _read_market()
        quantity = _read_number("تعداد فروش: ", allow_zero=False)
        price = _read_number(f"قیمت هر سهم ({Asset.MARKET_CURRENCIES[market]}): ", allow_zero=False)
        fees = _read_number("کارمزد کل (پیش‌فرض ۰): ", allow_zero=True, default=0)
        executed_at = _read_timestamp()
        realized = portfolio.record_sell(
            ticker, market, quantity, price, fees=fees, executed_at=executed_at
        )
    except (ValueError, KeyError) as error:
        print(f"ثبت فروش انجام نشد: {error}")
    else:
        currency = Asset.MARKET_CURRENCIES[market]
        print(f"فروش ثبت شد؛ سود/زیان تحقق‌یافته: {realized:.2f} {currency}")


def _show_history(portfolio):
    if not portfolio.transactions:
        print("هنوز معامله‌ای ثبت نشده است.")
        return
    print("\nتاریخچهٔ معاملات (به ترتیب ثبت):")
    for transaction in portfolio.transactions:
        if isinstance(transaction, CashTransaction):
            print(
                f"{transaction.executed_at.isoformat()} | {transaction.side} | "
                f"{transaction.amount:g} {transaction.currency}"
            )
            continue
        print(
            f"{transaction.executed_at.isoformat()} | {transaction.side} | "
            f"{transaction.ticker} [{transaction.market}/{transaction.currency}] | "
            f"{transaction.quantity:g} × {transaction.price:g} | "
            f"fees: {transaction.fees:g} {transaction.currency}"
        )


def _record_cash(portfolio):
    print("\nثبت وجه نقد")
    print("1. موجودی آغازین")
    print("2. واریز")
    print("3. برداشت")
    print("4. تطبیق با موجودی نقد فعلی")
    choice = input("انتخاب شما: ").strip()
    sides = {"1": "OPENING_CASH", "2": "CASH_DEPOSIT", "3": "CASH_WITHDRAWAL"}
    if choice not in sides:
        if choice != "4":
            print("عملیات وجه نقد لغو شد.")
            return
    try:
        currency = _read_currency()
        amount = _read_number(
            "مبلغ: " if choice != "4" else "ماندهٔ فعلی حساب کارگزاری: ",
            allow_zero=choice == "4",
        )
        executed_at = _read_timestamp()
        if choice == "4":
            difference = portfolio.reconcile_cash(currency, amount, executed_at=executed_at)
            print(f"موجودی تطبیق داده شد؛ تعدیل ثبت‌شده: {difference:+.2f} {currency}")
            return
        portfolio.record_cash(sides[choice], amount, currency, executed_at=executed_at)
    except ValueError as error:
        print(f"ثبت وجه نقد انجام نشد: {error}")
    else:
        print("رویداد وجه نقد ثبت شد.")


def _read_market():
    print("بازار: 1. آمریکا (USD)  2. ایران (IRR)")
    choice = input("انتخاب بازار: ").strip()
    if choice == "1":
        return "US"
    if choice == "2":
        return "IR"
    raise ValueError("بازار باید ۱ (آمریکا) یا ۲ (ایران) باشد.")


def _read_currency():
    print("ارز: 1. USD  2. IRR")
    choice = input("انتخاب ارز: ").strip()
    if choice == "1":
        return "USD"
    if choice == "2":
        return "IRR"
    raise ValueError("ارز باید ۱ (USD) یا ۲ (IRR) باشد.")


def _read_number(prompt, *, allow_zero, default=None):
    entered = input(prompt).strip()
    if not entered and default is not None:
        return default
    try:
        value = float(entered)
    except ValueError as error:
        raise ValueError("مقدار باید عددی باشد.") from error
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError("مقدار باید مثبت باشد." if not allow_zero else "مقدار نمی‌تواند منفی باشد.")
    return value


def _read_timestamp():
    entered = input("تاریخ و زمان ISO 8601 (خالی = اکنون UTC): ").strip()
    if not entered:
        return datetime.now(timezone.utc)
    if len(entered) == 10:
        entered = f"{entered}T00:00:00+00:00"
    return entered
