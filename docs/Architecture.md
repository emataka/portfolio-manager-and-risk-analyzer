# معماری پیشنهادی MVP

**وضعیت:** پیشنهاد اجرایی برای محصول تعریف‌شده در [Product MVP](Product_MVP.md). این سند معماری مقصد را مشخص می‌کند؛ پیاده‌سازی باید مرحله‌ای باشد تا CLI فعلی و منطق مالی موجود قابل‌استفاده بمانند.

## تصمیم معماری اصلی

در MVP از یک **ماژولار مونولیت** استفاده می‌کنیم: یک API پایتون، یک پایگاه دادهٔ رابطه‌ای و یک وب‌کلاینت واکنش‌گرا. فعلاً سرویس‌ها را به میکروسرویس تقسیم نمی‌کنیم؛ جداسازی ماژول‌ها برای تغییر و استقرار مستقل بعدی کافی است.

### پشتهٔ پیشنهادی

- **API:** FastAPI، چون هستهٔ فعلی Python است و API را می‌توان بدون قراردادن ورودی/خروجی وب در `core/` اضافه کرد.
- **پایگاه داده:** PostgreSQL برای دادهٔ چندکاربره و تراکنش‌های حسابداری.
- **دسترسی داده و تغییر schema:** SQLAlchemy و migrationهای نسخه‌دار؛ schema با `create_all` در محیط تولید به‌روزرسانی نشود.
- **رابط:** React و TypeScript به شکل وب‌کلاینت جدا از API، فارسی و RTL. PWA بعد از کارکرد پایه و بررسی نیاز نصب اضافه شود.
- **استقرار:** ابتدا یک محیط آزمایشی خصوصی؛ محیط production تنها بعد از بررسی امنیت، منبع داده، بازیابی نسخهٔ پشتیبان و الزامات حقوقی.

نسخهٔ دقیق کتابخانه‌ها هنگام ساخت نمونهٔ فنی انتخاب و در فایل‌های قفل وابستگی ثبت می‌شود؛ این سند به نسخهٔ خاصی وابسته نیست.

## مرز ماژول‌ها

```text
React web client (RTL)
        │ HTTPS / JSON
        ▼
FastAPI routes ── authentication / authorization
        │
        ├── application services (use cases)
        │      ├── portfolio and ledger
        │      ├── import / export
        │      ├── reports and performance
        │      └── market-data refresh
        │
        ├── core domain (current reusable Python logic)
        ├── repositories ── PostgreSQL
        └── provider adapters ── licensed/approved data sources
```

- `core/` منطق دامنه و محاسبات را نگه می‌دارد؛ نباید به FastAPI، React، HTTP یا نشست کاربر وابسته شود.
- لایهٔ route فقط احراز هویت، اعتبارسنجی درخواست و فراخوانی use case را انجام می‌دهد؛ محاسبهٔ مالی در route نوشته نشود.
- use caseها با repositoryها کار می‌کنند؛ جزئیات PostgreSQL از مدل دامنه جدا می‌ماند.
- CLI فعلی تا زمانی که وب‌کلاینت مسیر اصلی را پوشش دهد حفظ می‌شود و برای تست آفلاین هسته مفید است.
- به‌روزرسانی قیمت از درخواست گزارش جدا باشد؛ خرابی provider نباید درخواست خواندن یا آخرین قیمت ذخیره‌شده را از بین ببرد.

## مدل دادهٔ اولیه

- `users`: شناسه، شناسهٔ ورود، hash امن رمز و زمان‌های ایجاد/تغییر؛ رمز خام ذخیره نشود.
- `portfolios`: مالک، نام، بازار/واحد گزارش و زمان ایجاد.
- `transactions`: رویدادهای append-only شامل نوع، نماد، بازار، تعداد، قیمت، کارمزد، زمان اجرا و منبع ورود.
- `cash_transactions`: رویدادهای وجه نقد و تطبیق با همان پرتفوی و ارز.
- `instruments`: نماد، نام نمایشی، بازار، ارز و وضعیت فعال/غیرفعال.
- `quotes` و `price_bars`: قیمت، زمان بازار، زمان دریافت، منبع، واحد، نوع تعدیل و کیفیت/وضعیت داده.
- `audit_events`: تغییرات حساس مانند ورود فایل، اصلاح از طریق رویداد جبرانی، خروجی داده و عملیات حساب.

موجودی فعلی، بهای تمام‌شده و گزارش‌ها از رویدادهای دفتر معاملات ساخته یا با آن‌ها تطبیق داده می‌شوند؛ دو نسخهٔ مستقل و قابل‌ویرایش از یک حقیقت مالی ایجاد نکنیم. هر جدول متعلق به کاربر باید با `user_id` یا رابطهٔ مالکیت قابل‌اثبات محدود شود. شناسه‌های تصادفی به‌تنهایی مجوز دسترسی نیستند.

برای مبالغ و کارمزدهای ریالی، طراحی persistence باید دقت اعشاری ثابت را بررسی کند؛ آمار و ماتریس‌های عددی می‌توانند در محدودهٔ analytics از NumPy استفاده کنند. گردکردن خروجی باید در مرز نمایش تعریف شود و ارزش خام دفتر معاملات دست‌کاری نشود.

## قرارداد دادهٔ قیمت

هر quote/bar باید دست‌کم این موارد را حمل کند: `instrument`, `market`, `currency`, `price`, `market_timestamp`, `fetched_at`, `source`, `adjustment_type` و `quality_status`. گزارش باید بتواند قیمت قدیمی، قیمت تعدیل‌شده و دادهٔ ناقص را از هم تشخیص دهد. برای نسخهٔ ایران، تقویم بازار و رویدادهای شرکتی تا وقتی تأیید نشده‌اند نباید فرض‌شده یا پنهان بمانند.

تغییر provider یا روش تعدیل باید قرارداد داده را حفظ کند و با نمونه‌های ثبت‌شده و قابل‌بازتولید سنجیده شود. داده‌ای که مجوز استفاده/نمایش تجاری ندارد وارد محصول عمومی نشود.

## امنیت و حریم خصوصی از ابتدا

- همهٔ درخواست‌های داده با هویت کاربر احراز‌شده و مجوز همان منبع داده محدود شوند؛ `user_id` را از body درخواست نپذیریم.
- رمزها فقط با password hashing مناسب ذخیره شوند؛ کلیدها و connection stringها بیرون از مخزن نگهداری شوند.
- نشست امن، محدودیت تلاش ورود، محافظت CSRF برای cookie-based auth، TLS و کنترل نرخ درخواست برای مسیرهای حساس لازم‌اند.
- پشتیبان‌گیری رمزگذاری‌شده، آزمون بازیابی، سیاست نگهداری، حذف و خروجی گرفتن از داده بخشی از MVP است.
- هیچ رمز کارگزاری از کاربر درخواست یا در برنامه ذخیره نشود؛ ورود به کارگزاری فقط با API رسمی و توافق مجاز قابل بررسی است.

## API اولیه

قرارداد نسخهٔ اول می‌تواند این منابع را پوشش دهد:

- `POST /auth/...` و `DELETE /auth/session`
- `GET/POST /portfolios`
- `GET/POST /portfolios/{id}/transactions`
- `POST /portfolios/{id}/imports` و `GET /portfolios/{id}/exports`
- `GET /portfolios/{id}/summary` و `GET /portfolios/{id}/performance`
- `GET /instruments/search` و `GET /quotes`

هر پاسخ مالی باید ارز، بازهٔ گزارش و زمان آخرین قیمت را مشخص کند. خطاهای ورودی، دادهٔ قدیمی و محدودیت نرخ باید پاسخ قابل‌فهم و پایدار داشته باشند؛ stack trace یا اطلاعات حساب در پاسخ عمومی افشا نشود.

## مسیر مهاجرت از برنامهٔ فعلی

1. منطق هسته را در یک branch کاری از CLI جدا و قراردادهای مالی آن را مستند می‌کنیم.
2. repository و persistence جدید را کنار JSON فعلی می‌سازیم؛ JSON فعلی برای import/export شخصی باقی می‌ماند، نه پایگاه دادهٔ چندکاربره.
3. use caseهای پرتفوی را ابتدا با repository آزمایشی/SQLite محلی از API فراخوانی می‌کنیم.
4. پس از تثبیت قرارداد، PostgreSQL و migrationها را اضافه می‌کنیم.
5. وب‌کلاینت فقط از API استفاده می‌کند؛ منطق مالی در مرورگر تکرار نمی‌شود.
6. دادهٔ واقعی به production منتقل نمی‌شود تا مسیر مهاجرت، تطبیق، پشتیبان‌گیری و بازگشت بررسی شده باشد.

## دروازهٔ خروج از نمونهٔ فنی

نمونهٔ فنی زمانی آمادهٔ اتصال به وب‌کلاینت است که احراز هویت آزمایشی، یک مالک/پرتفوی/دفتر معاملات در پایگاه داده، migration از ابتدا تا انتها، یک گزارش قابل‌تطبیق و تست منفی دسترسی بین دو کاربر داشته باشد. تا پیش از آن، روی اپ بومی، اتصال کارگزاری یا پیشنهاد سرمایه‌گذاری کار نمی‌کنیم.

## English

**Status:** Proposed implementation architecture for the product in [Product MVP](Product_MVP.md). This describes the target architecture; implementation should be incremental so the current CLI and financial logic remain usable.

### Main architecture decision

Use a **modular monolith** for the MVP: one Python API, one relational database, and one responsive web client. Do not split into microservices yet; modular boundaries are sufficient for future independent changes and deployments.

### Proposed stack

- **API:** FastAPI, since the current core is Python and web input/output can be added without putting it into `core/`.
- **Database:** PostgreSQL for multi-user data and accounting transactions.
- **Data access and schema changes:** SQLAlchemy and versioned migrations; do not update production schemas with `create_all`.
- **Interface:** React and TypeScript as a web client separate from the API, in Persian and RTL. Add PWA behavior after core workflows and installation needs are validated.
- **Deployment:** begin with a private test environment. Use production only after security, data rights, backup recovery, and legal requirements are reviewed.

Select exact library versions when building the technical prototype and record them in dependency lock files; this design is not tied to a particular release.

### Module boundaries

```text
React web client (RTL)
        │ HTTPS / JSON
        ▼
FastAPI routes ── authentication / authorization
        │
        ├── application services (use cases)
        │      ├── portfolio and ledger
        │      ├── import / export
        │      ├── reports and performance
        │      └── market-data refresh
        │
        ├── core domain (current reusable Python logic)
        ├── repositories ── PostgreSQL
        └── provider adapters ── licensed/approved data sources
```

- Keep domain logic and calculations in `core/`; it must not depend on FastAPI, React, HTTP, or user sessions.
- Routes handle authentication, request validation, and calling use cases; do not put financial calculations in route handlers.
- Use cases depend on repositories; keep PostgreSQL details separate from domain models.
- Keep the current CLI until the web client covers the main workflows; it remains useful for offline core testing.
- Keep price refresh separate from report requests so a provider failure cannot break reads or discard the last saved price.

### Initial data model

- `users`: identifier, login identifier, secure password hash, and timestamps; never store raw passwords.
- `portfolios`: owner, name, market/reporting currency, and creation time.
- `transactions`: append-only events with type, ticker, market, quantity, price, fee, execution time, and entry source.
- `cash_transactions`: cash and reconciliation events scoped to the same portfolio and currency.
- `instruments`: ticker, display name, market, currency, and active/inactive state.
- `quotes` and `price_bars`: price, market time, retrieval time, source, unit, adjustment type, and quality status.
- `audit_events`: sensitive changes such as file import, compensating correction, data export, and account actions.

Derive current holdings, cost basis, and reports from the ledger or reconcile them against it; do not create two independently editable versions of the same financial truth. Scope every user-owned table by `user_id` or a provable ownership relationship. Random IDs alone do not grant access.

For IRR amounts and fees, evaluate fixed-precision storage in persistence; analytics may use NumPy. Define rounding at the display boundary and do not alter raw ledger values.

### Price-data contract

Every quote/bar should include at least `instrument`, `market`, `currency`, `price`, `market_timestamp`, `fetched_at`, `source`, `adjustment_type`, and `quality_status`. Reports must distinguish stale prices, adjusted prices, and incomplete data. For Iran, do not assume or hide market-calendar and corporate-action behavior until it is verified.

Provider or adjustment-method changes must preserve the data contract and be evaluated using recorded, reproducible fixtures. Do not use data publicly if its display or commercial-use rights are not established.

### Security and privacy from the start

- Authenticate every data request and authorize it against the user's identity; never accept `user_id` from the request body.
- Store passwords only with suitable password hashing; keep keys and connection strings outside the repository.
- Secure sessions, login-attempt limits, CSRF protection for cookie-based auth, TLS, and rate limits are needed for sensitive routes.
- Encrypted backups, restore tests, retention/deletion policy, and data export are MVP requirements.
- Never ask for or store a user's brokerage password; consider brokerage access only through an official API and permitted agreement.

### Initial API

The first API contract may cover:

- `POST /auth/...` and `DELETE /auth/session`
- `GET/POST /portfolios`
- `GET/POST /portfolios/{id}/transactions`
- `POST /portfolios/{id}/imports` and `GET /portfolios/{id}/exports`
- `GET /portfolios/{id}/summary` and `GET /portfolios/{id}/performance`
- `GET /instruments/search` and `GET /quotes`

Every financial response should state currency, report period, and latest quote time. Invalid input, stale data, and rate limits need stable, understandable responses; never expose stack traces or account details publicly.

### Migration from the current application

1. Separate core logic from the CLI in a working branch and document its financial contracts.
2. Build new repositories and persistence alongside the current JSON flow; retain JSON for personal import/export, not as a multi-user database.
3. Call portfolio use cases through an API using a test repository or local SQLite first.
4. Add PostgreSQL and migrations after the contract is stable.
5. Have the web client use only the API; do not duplicate financial logic in the browser.
6. Do not move real data into production until migration, reconciliation, backup, and rollback have been reviewed.

### Exit gate for the technical prototype

The prototype is ready to connect to a web client when it has test authentication, one user/portfolio/ledger in the database, an end-to-end migration, a reconcilable report, and a negative cross-user access test. Before that, do not work on native apps, brokerage connectivity, or investment recommendations.
