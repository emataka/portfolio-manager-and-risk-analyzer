# Development guide

## Local setup

Use Python 3.12, create a virtual environment, and install the project requirements:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Run the automated suite from the repository root:

```powershell
python -m pytest -q
```

The suite should use synthetic histories and must not call live market-data providers. GitHub Actions runs the same command on Python 3.12.

## Working on financial calculations

- Keep analytics and backtesting functions free of CLI input/output.
- Add a hand-computable synthetic example for every new formula or execution rule.
- Cover missing data, short histories, zero volatility, invalid weights, and optimizer failure paths.
- For backtest changes, assert that the signal window ends before the execution observation and account for costs at each rebalance.
- Preserve annualization conventions in [Financial Model](Financial_Model.md); update that document when a convention changes.

## Provider boundaries

Do not make unit tests depend on Yahoo Finance or the Tehran market provider. Test provider adapters with mocked responses or saved fixtures. Keep provider identity and adjustment assumptions visible in analysis results before using them for real decisions.

## Portfolio persistence

`core.persistence.portfolio_store` stores the current position snapshot, saved prices, quote currency, and transaction ledger as UTF-8 JSON with a schema version. Schema v1 snapshots infer currency from market; schema v1/v2 snapshots become opening balances because they contain no transaction ledger. The loader warns that legacy purchase-price units and earlier trade history must be reviewed. Schema v3/v4 replay the transaction ledger and check that reconstructed positions match the saved snapshot. Schema v4 also persists opening cash, deposits, withdrawals, cash reconciliations, and whether the cash history is complete. Cash proceeds/costs from buys and sells are derived from the trade ledger, and cash is reported in its native currency. Older files are marked as having incomplete cash history until reconciled with the current broker balance. Saving uses a temporary file and atomic replace; an existing file is not overwritten unless the caller explicitly opts in.

The transaction model is append-only. `Portfolio.record_buy`, `record_sell`, `record_opening_balance`, and `record_cash` validate chronological order. Trades update positions using weighted-average cost; their cash flows are included in same-currency cash balances. Cash can be negative when history omits initial funding or recorded trades exceed cash; surface that state clearly and do not silently assume margin is available. Use cash reconciliation to record the difference between ledger cash and a verified current broker balance. Do not change a historical transaction in place; correct it with a separately designed reversal/adjustment workflow so realized P/L remains auditable.

The CLI exposes save/load under **ذخیره/بارگذاری پرتفوی**. Files default to `portfolio.json` in the current working directory. Keep personal portfolio files out of version control.

## راهنمای توسعه

### راه‌اندازی محلی

از Python 3.12 استفاده کن، محیط مجازی بساز و وابستگی‌های پروژه را نصب کن:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

مجموعهٔ خودکار را از ریشهٔ مخزن اجرا کن:

```powershell
python -m pytest -q
```

آزمون‌ها باید از داده‌های مصنوعی استفاده کنند و به provider زندهٔ بازار متصل نشوند. GitHub Actions همین فرمان را با Python 3.12 اجرا می‌کند.

### کار روی محاسبات مالی

- توابع تحلیل و بک‌تست را از ورودی/خروجی CLI مستقل نگه‌دار.
- برای هر فرمول یا قاعدهٔ اجرای جدید، یک مثال مصنوعی با محاسبهٔ دستی اضافه کن.
- دادهٔ ناقص، تاریخچهٔ کوتاه، نوسان صفر، وزن نامعتبر و مسیرهای شکست optimizer را پوشش بده.
- در تغییرات بک‌تست، بررسی کن پنجرهٔ سیگنال پیش از تاریخ اجرا تمام شود و هزینه‌ها در هر بازتوازن لحاظ شوند.
- قراردادهای [مدل مالی](Financial_Model.md) را حفظ کن و هنگام تغییر آن‌ها سند را به‌روز کن.

### مرزهای provider

آزمون واحد را به Yahoo Finance یا provider بازار تهران وابسته نکن. adapterهای داده را با پاسخ mock یا fixture ذخیره‌شده بیازما. هویت provider و فرض‌های تعدیل باید پیش از استفادهٔ واقعی در نتایج تحلیل قابل‌مشاهده باشند.

### ماندگاری پرتفوی

`core.persistence.portfolio_store` snapshot فعلی دارایی‌ها، قیمت‌های ذخیره‌شده، ارز مظنه و دفتر معاملات را به JSON UTF-8 نسخه‌دار تبدیل می‌کند. snapshotهای schema v1 ارز را از بازار استنباط می‌کنند؛ فایل‌های v1/v2 به‌دلیل نداشتن دفتر معاملات به موجودی آغازین تبدیل می‌شوند. loader دربارهٔ واحد قیمت خرید legacy و سابقهٔ قبلی معامله هشدار می‌دهد. schemaهای v3/v4 دفتر معاملات را replay می‌کنند و سازگاری پوزیشن بازسازی‌شده با snapshot را بررسی می‌کنند. schema v4 وجه نقد آغازین، واریز، برداشت، تطبیق وجه نقد و کامل‌بودن سابقهٔ نقد را هم نگه می‌دارد. ورودی/خروجی خرید و فروش از دفتر معامله محاسبه و وجه نقد در ارز بومی گزارش می‌شود. فایل‌های قدیمی تا زمان تطبیق با ماندهٔ تأییدشدهٔ کارگزاری سابقهٔ ناقص دارند. ذخیره در فایل موقت و با جایگزینی اتمی انجام می‌شود؛ فایل موجود بدون تأیید صریح بازنویسی نمی‌شود.

مدل معامله append-only است. `Portfolio.record_buy`، `record_sell`، `record_opening_balance` و `record_cash` ترتیب زمانی را اعتبارسنجی می‌کنند. خرید و فروش پوزیشن را با میانگین موزون به‌روزرسانی و اثر نقدی را در ماندهٔ همان ارز ثبت می‌کند. وجه نقد ممکن است به‌علت نبود سرمایهٔ آغازین در تاریخچه یا خرید بیش از موجودی منفی شود؛ این وضعیت را آشکار کن و حاشیهٔ اعتباری را بی‌صدا فرض نکن. برای تطبیق نقد از ماندهٔ واقعی و تأییدشدهٔ کارگزاری استفاده کن. معاملهٔ تاریخی را درجا تغییر نده؛ برای حفظ سودوزیان تحقق‌یافته، اصلاح باید با رویداد معکوس/تعدیلی جداگانه و قابل‌ردیابی انجام شود.

در CLI گزینهٔ **ذخیره/بارگذاری پرتفوی** برای ذخیره و بارگذاری است. فایل پیش‌فرض `portfolio.json` در پوشهٔ کاری فعلی است. فایل‌های پرتفوی شخصی را وارد version control نکن.
