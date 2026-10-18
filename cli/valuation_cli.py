"""Record and review timestamped portfolio valuations in the local SQLite database."""

import math
import os
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.exc import SQLAlchemyError

from api.repository import SQLitePortfolioRepository
from core.analytics.time_weighted_return import (
    ValuationPoint,
    calculate_time_weighted_return,
)


def main():
    database_path = Path(os.environ.get("PORTFOLIO_API_DB", "data/portfolio.sqlite3")).expanduser()
    portfolio_id = os.environ.get("PORTFOLIO_API_PORTFOLIO_ID", "local").strip()
    if not database_path.is_file():
        print(f"پایگاه داده پیدا نشد: {database_path}")
        print("ابتدا پایگاه داده را با دستور api.migrate_json آماده کن.")
        return

    repository = SQLitePortfolioRepository(database_path)
    try:
        exists = repository.portfolio_exists(portfolio_id)
    except SQLAlchemyError as error:
        print(f"پایگاه داده آماده یا قابل‌خواندن نیست: {error}")
        print("مسیر پایگاه داده و اجرای مهاجرت را بررسی کن.")
        return
    if not exists:
        print(f"پرتفوی «{portfolio_id}» در پایگاه داده پیدا نشد.")
        print("ابتدا snapshot پرتفوی را با دستور api.migrate_json وارد کن.")
        return

    while True:
        print("\nتاریخچهٔ ارزش‌گذاری")
        print("1. ثبت ارزش‌گذاری")
        print("2. نمایش تاریخچه و بازده TWR")
        print("3. ابطال ردیف آزمایشی/اشتباه")
        print("4. بازگشت")
        choice = input("انتخاب شما: ").strip()
        if choice == "1":
            _record_valuation(repository, portfolio_id)
        elif choice == "2":
            _show_history(repository, portfolio_id)
        elif choice == "3":
            _void_valuation(repository, portfolio_id)
        elif choice == "4":
            return
        else:
            print("انتخاب نامعتبر است.")


def _record_valuation(repository, portfolio_id):
    try:
        currency = _read_currency()
        market_value = _read_finite_number(
            f"ارزش کل پرتفوی به {currency} (شامل وجه نقد): ", minimum=0
        )
        print("جریان خارجی بلافاصله پس از این زمان؛ واریز مثبت، برداشت منفی، بدون جریان = 0")
        external_flow = _read_finite_number("مبلغ جریان خارجی: ")
        timestamp = _read_timestamp()
        source = input("منبع ارزش‌گذاری (مثلاً صورت‌حساب کارگزاری): ").strip()
        stored = repository.record_valuation_point(
            portfolio_id,
            ValuationPoint(timestamp, market_value, currency, external_flow),
            source=source,
        )
    except (OSError, SQLAlchemyError, TypeError, ValueError) as error:
        print(f"ارزش‌گذاری ثبت نشد: {error}")
        return

    print(
        f"ارزش‌گذاری ثبت شد: #{stored.sequence} | {stored.point.timestamp.isoformat()} | "
        f"{stored.point.market_value:,.2f} {currency} | منبع: {stored.source}"
    )
    if stored.point.external_flow_after:
        print("این نقطه جریان خارجی دارد؛ برای محاسبهٔ TWR باید ارزش‌گذاری بعدی پس از جریان هم ثبت شود.")


def _void_valuation(repository, portfolio_id):
    try:
        currency = _read_currency()
        records = repository.get_valuation_points(portfolio_id, currency=currency)
        active_records = [record for record in records or [] if record.voided_at is None]
        if not active_records:
            print(f"رکورد فعالی برای ابطال در {currency} وجود ندارد.")
            return

        print("\nارزش‌گذاری‌های فعال:")
        for record in active_records:
            print(
                f"#{record.sequence} | {record.point.timestamp.isoformat()} | "
                f"{record.point.market_value:,.2f} {currency} | منبع: {record.source}"
            )
        try:
            sequence = int(input("شمارهٔ رکورد برای ابطال: ").strip())
        except ValueError as error:
            raise ValueError("شمارهٔ رکورد باید عدد صحیح باشد.") from error
        target = next((record for record in active_records if record.sequence == sequence), None)
        if target is None:
            raise ValueError("شمارهٔ واردشده در فهرست رکوردهای فعال نیست.")
        print(
            f"انتخاب شد: #{target.sequence} | {target.point.market_value:,.2f} {currency} | "
            f"{target.point.timestamp.isoformat()}"
        )
        reason = input("دلیل ابطال (مثلاً دادهٔ آزمایشی): ").strip()
        confirmation = input("برای ثبت ابطالِ غیرقابل‌حذف، عبارت VOID را وارد کن: ").strip()
        if confirmation != "VOID":
            print("ابطال لغو شد؛ هیچ تغییری ثبت نشد.")
            return
        correction = repository.void_valuation_point(
            portfolio_id,
            currency=currency,
            sequence=sequence,
            reason=reason,
        )
    except (OSError, SQLAlchemyError, TypeError, ValueError) as error:
        print(f"ابطال ثبت نشد: {error}")
        return

    print(
        f"رکورد #{correction.sequence} باطل شد؛ سابقه حفظ شده و در محاسبهٔ TWR استفاده نمی‌شود. "
        f"دلیل: {correction.void_reason}"
    )


def _show_history(repository, portfolio_id):
    try:
        currency = _read_currency()
        records = repository.get_valuation_points(portfolio_id, currency=currency)
    except (SQLAlchemyError, TypeError, ValueError) as error:
        print(f"تاریخچه خوانده نشد: {error}")
        return

    if records is None:
        print("پرتفوی در پایگاه داده پیدا نشد.")
        return
    if not records:
        print(f"برای {currency} ارزش‌گذاری ثبت نشده است.")
        return

    print(f"\nتاریخچهٔ {currency} (ارقام به همان ارز):")
    for record in records:
        point = record.point
        print(
            f"#{record.sequence} | {point.timestamp.isoformat()} | "
            f"ارزش: {point.market_value:,.2f} | جریان پس از ارزش‌گذاری: "
            f"{point.external_flow_after:+,.2f} | منبع: {record.source}"
        )
        if record.voided_at:
            print(f"  باطل‌شده در {record.voided_at.isoformat()} | دلیل: {record.void_reason}")

    active_records = [record for record in records if record.voided_at is None]
    if not active_records:
        print("هیچ نقطهٔ فعالی برای محاسبهٔ TWR وجود ندارد.")
    elif len(active_records) < 2:
        print("برای محاسبهٔ بازده TWR دست‌کم دو ارزش‌گذاری لازم است.")
    elif active_records[-1].point.external_flow_after != 0:
        print("TWR هنوز محاسبه نمی‌شود: آخرین نقطه جریان پس از ارزش‌گذاری دارد.")
    else:
        try:
            result = calculate_time_weighted_return(
                [record.point for record in active_records]
            )
        except ValueError as error:
            print(f"TWR قابل محاسبه نیست: {error}")
        else:
            print(f"بازده کل TWR در بازهٔ ثبت‌شده: {result:.2%}")


def _read_currency():
    print("ارز: 1. USD  2. IRR")
    choice = input("انتخاب ارز: ").strip()
    if choice == "1":
        return "USD"
    if choice == "2":
        return "IRR"
    raise ValueError("ارز باید ۱ (USD) یا ۲ (IRR) باشد.")


def _read_finite_number(prompt, *, minimum=None):
    entered = input(prompt).strip().replace(",", "")
    try:
        value = float(entered)
    except ValueError as error:
        raise ValueError("مقدار باید عددی باشد.") from error
    if not math.isfinite(value):
        raise ValueError("مقدار باید عددی متناهی باشد.")
    if minimum is not None and value < minimum:
        raise ValueError("ارزش پرتفوی نمی‌تواند منفی باشد.")
    return value


def _read_timestamp():
    entered = input("زمان ارزش‌گذاری ISO 8601 (خالی = اکنون UTC): ").strip()
    if not entered:
        return datetime.now(timezone.utc)
    if len(entered) == 10:
        entered = f"{entered}T00:00:00+00:00"
    try:
        timestamp = datetime.fromisoformat(entered)
    except ValueError as error:
        raise ValueError("زمان باید در قالب ISO 8601 باشد؛ مثلاً 2025-04-30T16:30:00+03:30.") from error
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValueError("منطقهٔ زمانی را مشخص کن؛ مثلاً +03:30 یا Z.")
    return timestamp


if __name__ == "__main__":
    main()
