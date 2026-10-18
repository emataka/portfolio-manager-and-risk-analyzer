# طراحی API / API Design

## فارسی

API فعلی یک نمونهٔ محلی و فقط‌خواندنی است؛ طرح مقصد برای بتای چندکاربره در [معماری پیشنهادی](Architecture.md) تعریف شده است. قرارداد عملیاتی فعلی در [نمونهٔ محلی API](API_Local_Prototype.md) آمده است.

### وضعیت پیاده‌سازی

- مسیرهای موجود: `GET /health`، `GET /api/v1/portfolio` و `GET /api/v1/portfolio/transactions`.
- API خلاصهٔ عملکرد TWR را به تفکیک ارز برمی‌گرداند؛ دوره از نقاط معتبر ثبت‌شده ساخته می‌شود و بازده سالانه‌سازی نمی‌شود.
- مسیرهای فعلی فقط‌خواندنی‌اند و یک پرتفوی محلی را از SQLite می‌خوانند.
- احراز هویت، مالکیت کاربر، محدودیت نرخ و دسترسی عمومی وجود ندارد؛ سرور را فقط روی `127.0.0.1` اجرا کن.

### قراردادهای مقصد

برای بتا، مسیرهای احراز هویت، پرتفوی، معاملات، import/export، خلاصه و عملکرد در [سند معماری](Architecture.md) پیشنهاد شده‌اند. پیش از افزودن مسیرهای نوشتنی باید مالکیت داده، احراز هویت، اعتبارسنجی درخواست، ثبت رخدادهای حساس و آزمون جداسازی حساب‌ها پیاده شوند. این طرح به معنی آماده‌بودن آن مسیرها نیست.

## English

The current API is a local, read-only prototype. The target multi-user beta design is described in [Proposed Architecture](Architecture.md), and the running prototype contract is documented in [Local API Prototype](API_Local_Prototype.md).

### Implemented status

- Available routes: `GET /health`, `GET /api/v1/portfolio`, and `GET /api/v1/portfolio/transactions`.
- The API returns a per-currency TWR summary based on valid stored observations. The return covers the recorded period and is not annualized.
- Current routes are read-only and read one local portfolio from SQLite.
- There is no authentication, user ownership enforcement, rate limiting, or public access control; bind the server to `127.0.0.1` only.

### Target contract

The proposed beta routes for authentication, portfolios, transactions, import/export, summaries, and performance are described in [Architecture](Architecture.md). Before adding write routes, implement data ownership, authentication, request validation, sensitive-event logging, and account-isolation tests. This proposal does not mean those routes are implemented or production-ready.
