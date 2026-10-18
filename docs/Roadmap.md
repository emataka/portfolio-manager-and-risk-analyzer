# نقشهٔ راه محصول

این نقشهٔ راه از محدودهٔ [Product MVP](Product_MVP.md) و معماری پیشنهادی [Architecture](Architecture.md) پیروی می‌کند. هدف نخست، بتای خصوصی ابزار مدیریت و تحلیل است؛ اجرای سفارش و مشاورهٔ شخصی در محدوده نیست.

## وضعیت کلی

- [x] ثبت محدودهٔ پیشنهادی MVP
- [x] تأیید شروع با سرمایه‌گذار حقیقی خودگردان، بازار ایران، سهام/وجه نقد و ورود دستی/CSV به‌عنوان فرض کاری
- [ ] تکمیل دروازه‌های داده و حسابداری برای بتا
- [ ] نمونهٔ فنی API و persistence چندکاربره
- [x] API محلی فقط‌خواندنی برای مشاهدهٔ یک پرتفوی ذخیره‌شده (بدون احراز هویت)
- [x] schema نسخه‌دار SQLite محلی و مهاجرت یک‌باره از snapshot JSON (روی دادهٔ نمونه اجرا و در آزمون خودکار پوشش داده شده؛ تک‌پرتفویی و محلی)
- [ ] وب‌کلاینت واکنش‌گرا
- [ ] بتای خصوصی و ارزیابی استفاده
- [ ] بررسی آمادگی عرضهٔ تجاری

## مرحلهٔ ۱ — هستهٔ مالی و دادهٔ قابل‌اعتماد

**خروجی:** گزارش قابل‌ردیابی که کاربر بتواند با دفتر مستقل تطبیق دهد.

- [ ] تعریف و پیاده‌سازی رویدادهای بازار ایران موردنیاز: تقسیم سهم، سود نقدی، افزایش سرمایه و توقف/بازگشایی؛ هر مورد تا منبع معتبر نیافته، با هشدار یا خارج از محاسبه بماند.
- [x] تکمیل import/export استاندارد CSV با preview، اعتبارسنجی، گزارش خطای سطر و جلوگیری از import تکراری.
- [ ] تکمیل valuation history و اعتبارسنجی بازده TWR؛ ذخیره/بازیابی، ورود دستی و نمایش وضعیت/بازده در API آماده است، اما تطبیق ورودی‌ها با نمونه‌های مستقل و اتصال منبع دادهٔ قابل‌اعتماد باقی مانده است.
- [x] پیاده‌سازی هستهٔ مستقل TWR با linking هندسی؛ ذخیرهٔ valuation، ورود دستی، حذف محاسباتی رکوردهای باطل و نمایش وضعیت/بازده در API انجام شده است.
- [ ] انتخاب منبع مجاز و پایدار برای قیمت سهام، شاخص مرجع و تاریخچه؛ ثبت منبع/زمان/کیفیت هر داده.
- [ ] اصلاح گزارش برای بازار تعطیل، quote قدیمی، گردش ناقص و محاسبات ریالی.
- [ ] ثبت آزمون‌های مرجع محاسباتی برای دفتر معاملات، هزینه‌ها، رویدادهای شرکتی و بازده.

**معیار خروج:** نمونه‌های محاسباتی مستقل تطبیق کنند و هر دادهٔ نامعتبر/قدیمی در UI قابل‌تشخیص باشد.

## مرحلهٔ ۲ — نمونهٔ فنی backend

**خروجی:** یک جریان end-to-end برای یک کاربر آزمایشی از API تا گزارش.

- [x] ایجاد اسکلت API محلی و تنظیم مسیر فایل پرتفوی از متغیر محیطی.
- [x] repository محلی SQLite و migration نسخه‌دار برای یک پرتفوی و دفتر رویداد append-only؛ مهاجرت JSON، idempotence و یکپارچگی دفتر آزمون شده‌اند.
- [ ] تعریف schema نسخه‌دار و migration برای کاربران، پرتفوی، ابزار، رویداد معامله و قیمت.
- [ ] ساخت use case و repository برای ایجاد پرتفوی و ثبت/خواندن معاملات.
- [ ] افزودن احراز هویت و کنترل مالکیت؛ آزمون دسترسی بین دو کاربر.
- [x] ساخت API محلی read-only برای خلاصهٔ پرتفوی و تاریخچه که از `core/` استفاده کند.
- [x] آزمون API از مسیر HTTP برای پاسخ‌ها، صفحه‌بندی، اعتبارسنجی query و خطاهای پیکربندی (با موفقیت اجرا شد).
- [ ] نگه‌داشتن CLI به‌عنوان مصرف‌کنندهٔ مستقل و حفظ آزمون‌های فعلی.

**معیار خروج:** با migration تازه، دو کاربر دادهٔ جدا داشته باشند؛ درخواست API گزارش با محاسبهٔ دفتر مرجع سازگار باشد.

## مرحلهٔ ۳ — وب‌کلاینت MVP

**خروجی:** کاربر آزمایشی بتواند بدون CLI پرتفوی خود را مدیریت کند.

- [ ] ساخت ورود/بازیابی حساب و layout فارسی RTL واکنش‌گرا.
- [ ] صفحهٔ پرتفوی با ارزش، وجه نقد، سودوزیان، ترکیب دارایی، منبع/زمان قیمت و هشدار داده.
- [ ] گردش ثبت معامله و وجه نقد.
- [ ] گردش ورود CSV با پیش‌نمایش و تأیید.
- [ ] صفحهٔ عملکرد با بازه، معیار بازار، افت و توضیح محدودیت‌ها.
- [ ] خروجی گرفتن، حذف حساب و نمایش/مدیریت consent.

**معیار خروج:** کاربران هدف بتوانند وظایف اصلی را بدون کمک مستقیم کامل کنند و اعداد را با سابقهٔ خود تطبیق دهند.

## مرحلهٔ ۴ — بتای خصوصی و آمادگی تجاری

**خروجی:** شواهدی برای تصمیم دربارهٔ عرضه و مدل درآمدی.

- [ ] استقرار محدود با پایش خطا، ثبت رخداد، پشتیبان‌گیری و تمرین بازیابی.
- [ ] تکمیل بررسی امنیت، حریم خصوصی، حق استفاده از داده و دامنهٔ قانونی محصول.
- [ ] دعوت از گروه کوچک کاربران هدف و ثبت فعال‌سازی، خطا، استفادهٔ تکراری و درخواست‌های پشتیبانی.
- [ ] اولویت‌بندی اصلاح‌ها بر اساس خطای مالی/امنیتی، سپس موانع استفاده و نیاز تکرارشونده.
- [ ] تصمیم مستند برای اشتراک، اپ بومی، پشتیبانی صندوق، اتصال رسمی کارگزاری یا توسعهٔ بازار.

**معیار خروج:** تصمیم عرضه بر اساس دادهٔ استفاده، دقت مالی و مجوز/دادهٔ قابل‌اتکا باشد؛ نه صرفاً تکمیل قابلیت‌ها.

## کارهایی که تا بعد از بتا متوقف می‌مانند

- سفارش‌گذاری، نگهداری وجوه، انتقال پول و دسترسی به حساب کارگزاری.
- توصیهٔ شخصی یا مدیریت خودکار پرتفوی.
- پشتیبانی چندارزی، بازار آمریکا، معاملات لحظه‌ای، شبکهٔ اجتماعی و هوش مصنوعی سرمایه‌گذاری.
- اپ بومی Android/iOS پیش از تأیید نیاز و استفادهٔ تکراری از وب‌کلاینت.

## اولویت اجرای بعدی

CSV دفتر معاملات با preview، اعتبارسنجی، خروجی، جلوگیری از ورود تکراری و تست خودکار پیاده شده است. مهاجرت محلی JSON به SQLite اجرا شده و این مرحله هنوز تک‌پرتفویی است و احراز هویت یا جداسازی کاربران ندارد. هستهٔ مستقل TWR، تاریخچهٔ append-only ارزش‌گذاری، ورود دستی و نمایش TWR با وضعیت کیفیت داده در گزارش API آماده‌اند. آزمون‌های مرجع چندجریانی و ادغام API افزوده شده‌اند و اکنون باید در محیط توسعه اجرا شوند؛ اتصال منبع دادهٔ قابل‌اعتماد و به‌روزرسانی قیمت همچنان جداگانه لازم است. پیش از هر مسیر نوشتنی HTTP یا دسترسی شبکه‌ای نیز مالکیت کاربر، احراز هویت و آزمون جداسازی کاربران لازم است.

## English

This roadmap follows the [Product MVP](Product_MVP.md) scope and the proposed [Architecture](Architecture.md). The first goal is a private beta for portfolio management and analysis; order execution and personalized advice are out of scope.

### Overall status

- [x] Document the proposed MVP scope.
- [x] Adopt a self-directed individual investor in Iran, equities/cash, and manual/CSV entry as working assumptions.
- [ ] Complete data and accounting gates for beta.
- [ ] Multi-user technical API and persistence prototype.
- [x] Local read-only API for viewing one saved portfolio; no authentication.
- [x] Versioned local SQLite schema and one-time JSON snapshot import; tested on sample data, still single-portfolio and local.
- [ ] Responsive web client.
- [ ] Private beta and usage evaluation.
- [ ] Commercial-readiness review.

### Stage 1 — Financial core and reliable data

**Outcome:** a traceable report users can reconcile with an independent ledger.

- [ ] Define and implement required Iran-market events: splits, cash dividends, capital increases, halts, and resumptions. Until a reliable source is found, warn or exclude them from calculations.
- [x] Complete standard transaction CSV import/export with preview, validation, row-level errors, and duplicate protection.
- [ ] Complete valuation history and validate TWR. Timestamped SQLite storage, manual entry, and API status/return output are ready; independent reference reconciliation and a reliable data source remain.
- [x] Implement standalone TWR with geometric linking. Valuation persistence, manual entry, computational exclusion of voided records, and API status/return output are implemented.
- [ ] Select permitted, stable sources for equity prices, benchmarks, and history; record source, timestamp, and quality.
- [ ] Improve reports for market closures, stale quotes, incomplete activity, and rial calculations.
- [ ] Add independent reference tests for ledger accounting, fees, corporate actions, and returns.

**Exit criterion:** independent calculation examples reconcile, and the UI identifies invalid or stale data.

### Stage 2 — Backend technical prototype

**Outcome:** one end-to-end API-to-report flow for a test user.

- [x] Create the local API skeleton and configure the portfolio file/database path through environment variables.
- [x] Local SQLite repository and versioned migrations for one portfolio and an append-only event ledger; JSON import, idempotence, and ledger integrity are covered.
- [ ] Define versioned user, portfolio, instrument, trade-event, and price schemas and migrations.
- [ ] Build use cases and repositories to create portfolios and record/read transactions.
- [ ] Add authentication and ownership checks; test cross-user access.
- [x] Local read-only API for portfolio summaries and history, using `core/`.
- [x] HTTP API tests for responses, pagination, query validation, and configuration errors.
- [ ] Keep the CLI as an independent client and preserve its existing tests.

**Exit criterion:** a fresh migration supports two isolated users, and the API report reconciles with a reference ledger.

### Stage 3 — MVP web client

**Outcome:** a test user can manage a portfolio without the CLI.

- [ ] Build sign-in/account recovery and responsive Persian RTL layout.
- [ ] Portfolio page with value, cash, P/L, allocation, quote source/time, and data warnings.
- [ ] Trade and cash-entry workflows.
- [ ] CSV import flow with preview and confirmation.
- [ ] Performance page with period, market reference, drawdown, and limitations.
- [ ] Data export, account deletion, and consent management.

**Exit criterion:** target users complete core tasks without direct help and can reconcile the reported figures.

### Stage 4 — Private beta and commercial readiness

**Outcome:** evidence to decide whether and how to launch.

- [ ] Limited deployment with error monitoring, audit logs, backups, and a recovery exercise.
- [ ] Complete security, privacy, data-rights, and legal-scope review.
- [ ] Invite a small target-user group and track activation, errors, repeat usage, and support requests.
- [ ] Prioritize financial/security errors, then usability barriers and repeated requests.
- [ ] Document decisions about subscription, native apps, fund support, official brokerage connectivity, or market expansion.

**Exit criterion:** launch decisions follow evidence on usage, financial accuracy, and permitted data—not feature count alone.

### Deferred until after beta

- Order placement, holding funds, money transfers, or brokerage-account access.
- Personalized advice or automated portfolio management.
- Multi-currency aggregation, US market, real-time trading, social features, or investment AI.
- Native Android/iOS apps before validating web usage and repeat demand.

### Current next priority

CSV transaction import/export, local JSON-to-SQLite migration, append-only valuation history, manual valuation entry, and TWR status/return in the read-only API are implemented. The project is still single-portfolio with no authentication or user isolation. Independent multi-flow and API tests have been added and must be run in the development environment. Reliable market-data sources and price timestamps remain separate requirements. Before any HTTP write route or network exposure, implement user ownership, authentication, and cross-user isolation tests.
