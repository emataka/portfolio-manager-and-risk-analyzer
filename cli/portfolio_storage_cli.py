from pathlib import Path

from core.persistence.portfolio_store import load_portfolio, save_portfolio


def manage_portfolio_storage(portfolio=None):
    print("\nذخیره‌سازی پرتفوی")
    print("1. ذخیرهٔ پرتفوی فعلی")
    print("2. بارگذاری پرتفوی از فایل")
    print("3. بازگشت")
    choice = input("انتخاب شما: ").strip()

    if choice == "1":
        if portfolio is None:
            print("هنوز پرتفویی در برنامه بارگذاری نشده است؛ چیزی برای ذخیره وجود ندارد.")
            print("برای ساخت پرتفوی نمونه، از منوی اصلی گزینهٔ ۱ را انتخاب کنید.")
            print("اگر فایل ذخیره‌شده دارید، همین‌جا گزینهٔ ۲ را برای بارگذاری انتخاب کنید.")
            return portfolio
        path = _portfolio_path()
        overwrite = False
        if path.exists():
            confirmation = input("فایل موجود است. بازنویسی شود؟ (y/N): ").strip().lower()
            overwrite = confirmation in {"y", "yes", "بله"}
            if not overwrite:
                print("ذخیره‌سازی لغو شد.")
                return portfolio
        try:
            save_portfolio(portfolio, path, overwrite=overwrite)
        except (OSError, TypeError, ValueError) as error:
            print(f"ذخیره‌سازی انجام نشد: {error}")
        else:
            print(f"پرتفوی در {path} ذخیره شد.")
        return portfolio

    if choice == "2":
        path = _portfolio_path()
        try:
            loaded_portfolio = load_portfolio(path)
        except (OSError, TypeError, ValueError) as error:
            print(f"بارگذاری انجام نشد: {error}")
            return portfolio
        print(f"پرتفوی از {path} بارگذاری شد.")
        for warning in loaded_portfolio.migration_warnings:
            print(f"هشدار سازگاری: {warning}")
        return loaded_portfolio

    return portfolio


def _portfolio_path():
    entered_path = input("مسیر فایل (پیش‌فرض: portfolio.json): ").strip()
    return Path(entered_path) if entered_path else Path("portfolio.json")
