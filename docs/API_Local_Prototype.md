# نمونهٔ محلی API

این API نخستین اتصال بین مدل مالی موجود و یک کلاینت وب است. فعلاً فقط‌خواندنی است، یک پایگاه دادهٔ SQLite محلی را می‌خواند و احراز هویت یا جداسازی کاربر ندارد؛ برای استفادهٔ محلی و توسعه است و آمادهٔ استقرار عمومی نیست.

## اجرا در PowerShell

از پوشهٔ اصلی پروژه:

```powershell
py -3.14 -m pip install -r requirements-web.txt
$env:PORTFOLIO_API_FILE = (Resolve-Path .\ledger-v4-reconciled.json).Path
$env:PORTFOLIO_API_DB = (Join-Path (Get-Location) 'data\portfolio.sqlite3')
py -3.14 -m api.migrate_json
py -3.14 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

فرض این است که وابستگی‌های اصلی پروژه قبلاً نصب شده‌اند. `requirements-web.txt` وابستگی‌های API و پایگاه داده را اضافه می‌کند و دوباره وابستگی‌های بازار را نصب نمی‌کند. مسیر فایل باید به یک فایل JSON معتبر باشد که برنامهٔ فعلی ذخیره کرده است. دستور مهاجرت، فایل را اعتبارسنجی می‌کند و فقط یک‌بار وارد SQLite می‌کند. اگر همان شناسه قبلاً با داده‌ای متفاوت پر شده باشد، مهاجرت از جایگزینی آن خودداری می‌کند. اگر فایل دیگری داری، نام آن را در دستور PowerShell جایگزین کن. متغیرهای محیطی تا پایان همان نشست PowerShell فعال می‌مانند.

پس از نصب وابستگی‌های پایه و API، برای آزمون‌های HTTP واقعی وابستگی توسعه را نصب و کل مجموعه را اجرا کن. این فایل فقط وابستگی کلاینت تست را اضافه می‌کند تا نصب دوبارهٔ وابستگی‌های دادهٔ بازار لازم نشود:

```powershell
py -3.14 -m pip install -r requirements-test.txt
py -3.14 -m pytest -q
```

میزبان `127.0.0.1` را تغییر نده؛ API در این مرحله ورود و مجوز دسترسی ندارد. فایل نمونهٔ حاوی دادهٔ واقعی خود را به مخزن اضافه نکن.

## مسیرها

- `GET /health`: وضعیت API و اینکه فایل پرتفوی پیکربندی شده است یا نه.
- `GET /api/v1/portfolio`: دارایی‌ها، خلاصهٔ جداگانه به تفکیک ارز، عملکرد TWR بر مبنای ارزش‌گذاری‌های فعال، سطح تمرکز و هشدارهای کیفیت داده.
- `GET /api/v1/portfolio/transactions?limit=50&offset=0`: تاریخچهٔ دفتر معاملات با صفحه‌بندی؛ `limit` بین ۱ تا ۱۰۰ است.
- `GET /docs`: مستندات تعاملی OpenAPI در محیط محلی.

گزارش مبالغ ارزهای مختلف را با هم جمع نمی‌کند. عملکرد TWR فقط وقتی `available` است که دست‌کم دو ارزش‌گذاری معتبر و یک زنجیرهٔ زمانی قابل محاسبه وجود داشته باشد؛ در غیر این صورت، وضعیت، تعداد نقاط و دلیل محدودیت در پاسخ می‌آید. بازده، بازده کل بازه است و سالانه‌سازی نمی‌شود. ارزش‌گذاری‌های باطل‌شده از محاسبه کنار گذاشته می‌شوند و تعدادشان جداگانه گزارش می‌شود. زمان آخرین قیمت در مدل فعلی ذخیره نمی‌شود؛ در پاسخ API این محدودیت صریح است و هشدار قیمت نمایش داده می‌شود. `generated_at` زمان ساخت پاسخ است و نباید زمان به‌روزرسانی قیمت تلقی شود.

## محدودیت‌های این مرحله

- API هر درخواست را از یک پایگاه دادهٔ SQLite محلی می‌خواند؛ JSON فقط منبع انتقال اولیه است. repository فعلی هنوز چندکاربره نیست.
- احراز هویت، مجوز دسترسی، rate limit و ثبت رخداد ندارد؛ به اینترنت یا شبکهٔ عمومی متصلش نکن.
- مسیر نوشتن، ورود CSV از طریق HTTP، ثبت معامله، به‌روزرسانی قیمت یا توصیهٔ سرمایه‌گذاری در API وجود ندارد.
- پیش از بتای چندکاربره باید schema و migration پایگاه داده، مالکیت داده، احراز هویت و آزمون جداسازی کاربران پیاده شوند.

## English

This API is the first connection between the existing financial model and a web client. It is read-only, reads one local SQLite database, and has no authentication or user isolation. It is for local development and is not ready for public deployment.

### Run in PowerShell

From the project root:

```powershell
py -3.14 -m pip install -r requirements-web.txt
$env:PORTFOLIO_API_FILE = (Resolve-Path .\portfolio.json).Path
$env:PORTFOLIO_API_DB = (Join-Path (Get-Location) 'data\portfolio.sqlite3')
py -3.14 -m api.migrate_json
py -3.14 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

This assumes the project's base dependencies are installed. `requirements-web.txt` adds the API and database dependencies without reinstalling market-data packages. The source file must be a valid JSON portfolio saved by the application. The import command validates the file and imports it into SQLite once. If the same portfolio ID already contains different data, the import refuses to replace it. Replace the sample filename in PowerShell if your file has another name. Environment variables remain active for the current PowerShell session.

After installing base and API dependencies, install the test dependency and run the full suite for real HTTP tests. This file adds only the test client dependency:

```powershell
py -3.14 -m pip install -r requirements-test.txt
py -3.14 -m pytest -q
```

Keep the server bound to `127.0.0.1`; this prototype has no login or access control. Do not add a real-data sample file to the repository.

### Routes

- `GET /health`: API status and whether a portfolio is configured.
- `GET /api/v1/portfolio`: assets, currency-separated summaries, TWR based on active valuation points, concentration levels, and data-quality warnings.
- `GET /api/v1/portfolio/transactions?limit=50&offset=0`: paginated transaction history; `limit` must be between 1 and 100.
- `GET /docs`: interactive OpenAPI documentation for local development.

The report never adds values across currencies. TWR is `available` only with at least two valid valuation points and a calculable time series; otherwise the response includes a status, observation counts, and an explanation. The return is for the stored period and is not annualized. Voided observations are excluded and counted separately. The current model does not store the timestamp of the latest quote; the API states this limitation and warns that prices may be stale. `generated_at` is the response-generation time, not a quote update time.

### Current limits

- Each request reads one local SQLite database; JSON is only the initial transfer source. The repository is not multi-user.
- There is no authentication, authorization, rate limiting, or audit-event logging; do not expose it to the internet or a public network.
- The API has no write route, CSV import over HTTP, trade entry, price update, or investment recommendation.
- Before a multi-user beta, implement database ownership, authentication, schema migrations, and cross-user isolation tests.
