# قالب CSV دفتر معاملات

از زیرمنوی **دفتر معاملات** می‌توان قالب CSV ساخت، دفتر را خروجی گرفت یا فایل را وارد کرد. فایل باید UTF-8 باشد؛ قالب تولیدشده با BOM برای بازشدن در spreadsheetها سازگارتر است. جداکنندهٔ ستون‌ها کاما است و اعداد باید با رقم لاتین، نقطهٔ اعشاری و بدون جداکنندهٔ هزارگان نوشته شوند.

## ستون‌ها

ترتیب و نام ستون‌ها باید دقیقاً مطابق این سرستون باشد:

```csv
record_type,side,ticker,market,quantity,price,fees,amount,currency,executed_at
```

| ستون | تعریف |
|---|---|
| `record_type` | `TRADE` یا `CASH` |
| `side` | برای معامله: `OPENING_BALANCE`، `BUY`، `SELL`. برای وجه نقد: `OPENING_CASH`، `CASH_DEPOSIT`، `CASH_WITHDRAWAL` یا `CASH_RECONCILIATION` |
| `ticker` | نماد در رویداد `TRADE`؛ در رویداد `CASH` خالی |
| `market` | `IR` برای بورس ایران یا `US`؛ در رویداد `CASH` خالی |
| `quantity` | تعداد مثبت در رویداد `TRADE`؛ در رویداد `CASH` خالی |
| `price` | قیمت مثبت هر سهم در رویداد `TRADE`؛ در رویداد `CASH` خالی |
| `fees` | کارمزد نامنفی رویداد معامله؛ اگر صفر است `0` بنویس. در رویداد `CASH` خالی |
| `amount` | فقط برای وجه نقد؛ در `CASH_RECONCILIATION` مقدار signed تعدیل دفتر است، نه ماندهٔ واقعی کارگزاری |
| `currency` | `IRR` برای بازار ایران یا `USD` برای آمریکا |
| `executed_at` | تاریخ‌وساعت ISO 8601 با منطقهٔ زمانی، مثل `2025-01-02T09:30:00+03:30` |

نمونه:

```csv
record_type,side,ticker,market,quantity,price,fees,amount,currency,executed_at
TRADE,OPENING_BALANCE,نماد,IR,10,1000,0,,IRR,2025-01-01T09:00:00+03:30
CASH,OPENING_CASH,,,,,,1000000,IRR,2025-01-01T09:00:00+03:30
TRADE,BUY,نماد,IR,2,1100,100,,IRR,2025-01-02T09:00:00+03:30
```

## قواعد واردکردن

- رویدادها باید از قدیمی به جدید باشند و قبل از آخرین رویداد ثبت‌شده قرار نگیرند.
- فروش باید با موجودی همان نماد و بازار سازگار باشد؛ ارز هر بازار ثابت است.
- همهٔ ردیف‌ها پیش از ثبت بررسی می‌شوند. وجود خطای داده یا ناسازگاری دفتر باعث می‌شود هیچ ردیفی ثبت نشود.
- ردیف‌هایی که از نظر نوع، نماد، بازار، تعداد/مبلغ، قیمت، کارمزد، ارز و زمان دقیقاً با رویداد موجود یکسان‌اند تکراری شمرده و رد می‌شوند. برای واردکردن چند معاملهٔ واقعاً جداگانه، زمان اجرای متمایز و درست هر معامله را ثبت کن.
- برنامه ابتدا پیش‌نمایش می‌دهد و تنها پس از تأیید صریح کاربر همهٔ ردیف‌های معتبر را یکجا ثبت می‌کند.
- فایل CSV اطلاعات مالی دارد؛ آن را در مخزن کد یا محل عمومی ذخیره نکن.

## English

The **Transaction Ledger** submenu can generate a CSV template, export the ledger, or import a CSV file. Files must be UTF-8; the generated template uses a BOM for better spreadsheet compatibility. Columns are comma-separated. Numbers must use Latin digits, a period as the decimal separator, and no thousands separators.

### Columns

Column names and order must exactly match this header:

```csv
record_type,side,ticker,market,quantity,price,fees,amount,currency,executed_at
```

| Column | Definition |
|---|---|
| `record_type` | `TRADE` or `CASH` |
| `side` | For trades: `OPENING_BALANCE`, `BUY`, `SELL`. For cash: `OPENING_CASH`, `CASH_DEPOSIT`, `CASH_WITHDRAWAL`, or `CASH_RECONCILIATION` |
| `ticker` | Symbol for a `TRADE` event; blank for `CASH` |
| `market` | `IR` for Iran or `US`; blank for `CASH` |
| `quantity` | Positive quantity for `TRADE`; blank for `CASH` |
| `price` | Positive per-share price for `TRADE`; blank for `CASH` |
| `fees` | Non-negative trade fee; use `0` when there is no fee. Blank for `CASH` |
| `amount` | Used only for cash. For `CASH_RECONCILIATION`, this is the signed ledger adjustment, not the broker's actual balance |
| `currency` | `IRR` for Iran or `USD` for the US market |
| `executed_at` | ISO 8601 date and time with a timezone, such as `2025-01-02T09:30:00+03:30` |

Example:

```csv
record_type,side,ticker,market,quantity,price,fees,amount,currency,executed_at
TRADE,OPENING_BALANCE,Symbol,IR,10,1000,0,,IRR,2025-01-01T09:00:00+03:30
CASH,OPENING_CASH,,,,,,1000000,IRR,2025-01-01T09:00:00+03:30
TRADE,BUY,Symbol,IR,2,1100,100,,IRR,2025-01-02T09:00:00+03:30
```

### Import rules

- Events must be ordered from oldest to newest and cannot precede the latest event already recorded.
- A sale must be supported by the position in the same symbol and market; each market has a fixed currency.
- All rows are validated before import. Any data error or ledger inconsistency prevents the entire import.
- Rows that exactly match an existing event by type, symbol, market, quantity/amount, price, fee, currency, and timestamp are treated as duplicates and skipped. Distinct real trades need their own accurate execution timestamps.
- The application previews the file and imports all valid rows atomically only after explicit user confirmation.
- CSV files contain financial information; do not store them in the code repository or a public location.
