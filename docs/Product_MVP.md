# تعریف محصول و محدودهٔ MVP

**وضعیت سند:** پیشنهاد محصولی نسخهٔ ۰٫۱؛ فرض‌های این سند باید با کاربر و الزامات بازار اعتبارسنجی شوند.

## چشم‌انداز

یک ابزار فارسی و قابل‌اعتماد برای ثبت دارایی‌های شخصی در بازار سرمایهٔ ایران و فهمیدن ارزش، ترکیب، سودوزیان و ریسک آن‌ها؛ در نسخهٔ اول، محصول نقش کارگزاری یا مدیر سرمایه را ندارد.

## کاربر هدف

سرمایه‌گذار حقیقی خودگردان در ایران که در یک یا چند کارگزاری حساب دارد، دارایی‌هایش را با فایل یا ورود دستی ثبت می‌کند و برای دیدن تصویر یکپارچه و قابل‌فهم از پرتفوی خود به ابزار نیاز دارد. کاربر باید بتواند اعداد گزارش را تا معامله، قیمت و زمان آخرین به‌روزرسانی دنبال کند.

### مسئله‌ای که حل می‌کنیم

«دارایی‌ها و سوابق من پراکنده‌اند؛ می‌خواهم بدون واگذاری پول یا اختیار معامله، بدانم الان چه دارم، بهای تمام‌شده و سودوزیانم چیست و عملکرد پرتفوی در مقایسه با یک معیار بازار چگونه بوده است.»

## بازار شروع و جایگاه محصول

- **بازار شروع پیشنهادی:** بورس اوراق بهادار تهران، با گزارش مبالغ به ریال و نمایش روشن واحد پول.
- **دارایی نسخهٔ اول:** سهام پذیرفته‌شده و وجه نقد ریالی. صندوق‌ها فقط پس از اطمینان از منبع قیمت/NAV و رفتار تقسیم سود و ابطال وارد محدوده شوند.
- **ورود اطلاعات:** ثبت دستی و واردکردن فایل استاندارد CSV با پیش‌نمایش و اعتبارسنجی. اتصال خودکار کارگزاری در نسخهٔ اول نیست.
- **موقعیت:** ابزار مستقلِ مدیریت و تحلیل پرتفوی؛ مکمل سامانهٔ کارگزاری، نه جایگزین آن.
- **پلتفرم پیشنهادی:** وب واکنش‌گرا یا PWA برای بتای اولیه؛ اپ بومی Android/iOS بعد از مشاهدهٔ استفادهٔ واقعی و نیاز کاربران.

## قابلیت‌های داخل MVP

### ۱. حساب و حریم خصوصی

- ثبت‌نام و ورود امن، بازیابی حساب، خروج از نشست‌ها و حذف حساب.
- هر کاربر فقط به پرتفوی‌های خودش دسترسی داشته باشد؛ جداسازی دادهٔ کاربران در لایهٔ API و پایگاه داده آزمون‌پذیر باشد.
- نمایش شفاف رضایت‌ها، هدف استفاده از داده، سیاست نگهداری و روش درخواست خروجی/حذف داده.

### ۲. پرتفوی و دفتر معاملات

- ایجاد یک یا چند پرتفوی با واحد پول و بازار مشخص.
- ثبت موجودی آغازین، خرید، فروش، کارمزد، واریز، برداشت و تطبیق وجه نقد.
- واردکردن CSV با الگوی منتشرشده، پیش‌نمایش، گزارش خطای ردیف‌ها و جلوگیری از ثبت تکراری ناخواسته.
- قرارداد فایل در [قالب CSV دفتر معاملات](Transaction_CSV_Format.md) آمده است.
- امکان مشاهده و خروجی گرفتن از تاریخچهٔ معاملات؛ اصلاح سوابق با ردپای حسابرسی، نه بازنویسی خاموش تاریخچه.

### ۳. قیمت و کیفیت داده

- نمایش قیمت، منبع، زمان دریافت و وضعیت تازه/قدیمی بودن برای هر دارایی.
- نمایش هشدار و نگه‌داشتن آخرین قیمت معتبر هنگام شکست دریافت؛ قیمت قدیمی نباید به‌عنوان قیمت زنده نمایش داده شود.
- ثبت نسخه و منبع دادهٔ تاریخی، منطقهٔ زمانی، واحد پول و روش تعدیل رویدادهای شرکتی.
- انتخاب معیار بازار پس از تأیید منبع قابل‌اتکا و مجاز برای شاخص و تاریخچهٔ تعدیل‌شده.

### ۴. داشبورد و گزارش

- ارزش کل اوراق و وجه نقد، جداگانه به ریال؛ بدون جمع‌زدن واحدهای پول متفاوت.
- بهای تمام‌شده، سودوزیان تحقق‌یافته و تحقق‌نیافته، بازده پرتفوی و ترکیب دارایی‌ها.
- نمودار عملکرد در بازهٔ انتخابی، افت سرمایه، نوسان و تمرکز پرتفوی؛ هر معیار همراه تعریف کوتاه و بازهٔ داده.
- مقایسه با شاخص بازار در دورهٔ مشترک، با نمایش واضح تفاوت معیار و پرتفوی.
- خروجی CSV و گزارش قابل‌خواندن برای نگهداری شخصی.
- بازده‌های دوره‌ای باید جریان‌های نقدی بیرونی را لحاظ کنند؛ تا تکمیل و اعتبارسنجی بازده زمان‌وزن، هر بازده ساده باید با نام و محدودیت دقیق خودش ارائه شود.

### ۵. توضیح‌پذیری و کنترل کاربر

- نشان‌دادن اینکه هر جمع، وزن، سودوزیان و شاخص چگونه از معاملات و قیمت‌ها ساخته شده است.
- هشدار دربارهٔ دادهٔ ناقص، تاریخچهٔ ناقص وجه نقد، قیمت قدیمی، واحد نامشخص و دورهٔ ناکافی.
- هیچ معامله یا تغییر پرتفویی بدون اقدام صریح کاربر انجام نشود.

## خارج از محدودهٔ نسخهٔ اول

- ارسال سفارش خرید/فروش، نگهداری پول یا دارایی کاربر، انتقال وجه و اتصال به حساب معاملاتی.
- مشاورهٔ شخصی‌سازی‌شدهٔ خریدوفروش، توصیهٔ خودکار یا مدیریت اختیاری پرتفوی.
- بازار آمریکا، تبدیل ارز و جمع‌زدن دارایی‌های چندارزی در یک رقم.
- معاملات لحظه‌ای، شبکهٔ اجتماعی، کپی‌ترید، سیگنال‌فروشی، اهرم و مشتقات.
- صندوق‌ها و دارایی‌های جایگزین تا زمانی که داده و حسابداری رویدادهای آن‌ها قابل‌اتکا نشده باشد.
- دستیار هوش مصنوعی که توصیهٔ سرمایه‌گذاری شخصی ارائه کند.

این موارد از نظر فنی برای همیشه ممنوع نیستند؛ هرکدام نیازمند اعتبارسنجی محصول، داده، امنیت و در موارد مرتبط بررسی مجوزهای قانونی جداگانه‌اند.

## معیارهای پذیرش بتای خصوصی

بتا زمانی آمادهٔ دعوت از کاربران محدود است که:

1. ثبت دستی و ورود CSV روی دادهٔ نمونه، شامل خرید، فروش، کارمزد و جریان نقدی، با دفتر مرجع مستقل تطبیق داشته باشد.
2. همهٔ گزارش‌های مالی واحد پول و زمان آخرین قیمت را نشان دهند و هیچ‌گاه قیمت ناموفق را تازه جلوه ندهند.
3. آزمون‌های محاسباتی برای کارمزد، تقسیم سهم، سود نقدی، بازده با جریان نقدی، بازار تعطیل و دادهٔ ناقص داشته باشند.
4. آزمون جداسازی حساب‌ها ثابت کند کاربر نمی‌تواند دادهٔ کاربر دیگر را بخواند یا تغییر دهد.
5. پشتیبان‌گیری و بازیابی، ثبت رخدادهای حساس، حذف حساب و خروجی گرفتن از داده به‌صورت عملی بررسی شده باشند.
6. منبع داده و حق استفاده از آن، متن حریم خصوصی، شرایط استفاده، متن معرفی محصول و مرز قابلیت‌های تحت نظارت بررسی شده باشند.
7. در یک بتای محدود، کاربران بتوانند بدون راهنمایی مستقیم پرتفوی بسازند، داده وارد کنند و گزارش را تفسیر کنند؛ موانع پرتکرار ثبت و اصلاح شوند.

## ریسک‌های تجاری و دروازهٔ عرضه

- **مجوز و دامنهٔ خدمت:** نمایش تحلیلی، پیشنهاد شخصی، مشاوره، سبدگردانی و اجرای سفارش ممکن است وضعیت‌های حقوقی متفاوتی داشته باشند. پیش از عرضهٔ عمومی یا پولی، دامنهٔ دقیق خدمت باید با مشاور حقوقی آشنا به مقررات بازار سرمایهٔ ایران بررسی و مکتوب شود. متن تبلیغاتی یا سلب مسئولیت به‌تنهایی جای این بررسی را نمی‌گیرد.
- **حق استفاده از داده:** دریافت فنی داده به معنی داشتن حق بازتوزیع یا استفادهٔ تجاری نیست. قرارداد، محدودیت نمایش و ذخیره‌سازی هر منبع باید جداگانه بررسی شود.
- **مسئولیت دقت:** خطای قیمت، رویداد شرکتی یا واحد پول می‌تواند گزارش مالی گمراه‌کننده بسازد؛ منشأ داده و محدودیت هر خروجی باید قابل‌ردیابی باشد.
- **امنیت:** دارایی و رفتار سرمایه‌گذاری دادهٔ حساس است؛ طراحی دسترسی، رمزنگاری، مدیریت اسرار، پشتیبان‌گیری و پاسخ به رخداد باید پیش از بتا عملی شود.
- **مدل درآمدی پیشنهادی برای اعتبارسنجی:** بتای رایگان و سپس اشتراک برای گزارش‌ها و امکانات تحلیلی؛ دریافت کارمزد وابسته به معامله یا مدیریت دارایی خارج از محدودهٔ MVP است.

## نقشهٔ اجرا

### مرحلهٔ صفر — اعتبارسنجی محصول و دامنه

- مصاحبه با ۵ تا ۱۰ سرمایه‌گذار هدف دربارهٔ روش فعلی ثبت دارایی و گزارش موردنیاز.
- تهیهٔ نمونه CSV از گردش‌های واقعی با حذف اطلاعات هویتی و حسابی.
- بررسی اولیهٔ حق استفاده از داده و مرز حقوقی قابلیت‌ها.
- تأیید دامنهٔ بازار و دارایی‌های نسخهٔ اول.

### مرحلهٔ یک — قابل‌اعتماد کردن هسته

- تثبیت حسابداری دفتر معاملات، وجه نقد، کارمزد و رویدادهای شرکتی.
- تعریف عملکرد زمان‌وزن و معیارهای مقایسه، همراه با منبع و کیفیت داده.
- تکمیل import/export و هشدارهای دادهٔ قدیمی/ناقص.

### مرحلهٔ دو — بتای وب چندکاربره

- API و پایگاه دادهٔ تولیدی، ورود امن، جداسازی کاربران و ثبت رخداد.
- رابط وب واکنش‌گرا برای گردش‌های MVP.
- استقرار محدود با پایش، پشتیبان‌گیری، بازیابی و مسیر دریافت بازخورد.

### مرحلهٔ سه — آمادگی تجاری

- تکمیل بررسی حقوقی و قرارداد داده، حریم خصوصی، شرایط استفاده، پشتیبانی و پاسخ به رخداد.
- اندازه‌گیری فعال‌سازی، استفادهٔ تکراری، خطاهای داده و تمایل به پرداخت.
- تصمیم دربارهٔ اشتراک، اپ بومی، اتصال رسمی کارگزاری یا گسترش دارایی‌ها فقط براساس شواهد بتا.

## فرض‌ها و تصمیم‌های نیازمند تأیید

این نسخه با فرض شروع از **سرمایه‌گذار حقیقی خودگردان در ایران** و ساخت **ابزار read-only برای تحلیل و مدیریت شخصی** نوشته شده است. هنوز باید دربارهٔ موارد زیر تصمیم بگیریم:

- آیا کاربر هدف همین سرمایه‌گذار خودگردان است یا مشاور/تیم مالی؟
- آیا شروع فقط با سهام و وجه نقد کافی است یا صندوق‌های سرمایه‌گذاری باید از روز اول داخل محدوده باشند؟
- آیا وب/PWA برای بتا کافی است یا نسخهٔ Android از ابتدا الزام محصول است؟
- آیا هدف بلندمدت، محصول مستقل تحلیلی است یا همکاری/اتصال رسمی با کارگزاری؟

پیشنهاد اولیه: سهام و وجه نقد، ثبت دستی/CSV، وب واکنش‌گرا و بدون سفارش‌گذاری؛ این محدوده زودتر قابل‌آزمایش است و ریسک عملیاتی کمتری دارد.

## English

**Document status:** Product proposal, version 0.1. Assumptions in this document still need validation with users and against market requirements.

### Vision

A reliable Persian-language tool for recording personal Iranian-market holdings and understanding their value, composition, profit and loss, and risk. The first release is not a brokerage or investment manager.

### Target user

A self-directed individual investor in Iran with accounts at one or more brokerages, who records holdings manually or by file and needs a clear, consolidated portfolio view. Users should be able to trace reported figures to transactions, prices, and their latest update time.

**Problem to solve:** “My assets and records are scattered. Without handing over money or trading authority, I want to know what I own, my cost basis and profit/loss, and how my portfolio performed against a market reference.”

### Initial market and product position

- **Proposed initial market:** Tehran Stock Exchange, reporting amounts in rial with the currency unit clearly shown.
- **First-release assets:** listed equities and IRR cash. Add funds only after confirming price/NAV sources and how distributions and redemptions are handled.
- **Data entry:** manual entry and standard CSV import with preview and validation. Automatic brokerage connectivity is out of scope for the first release.
- **Positioning:** an independent portfolio-management and analysis tool that complements a brokerage system rather than replacing it.
- **Proposed platform:** responsive web or PWA for the private beta; consider native Android/iOS after observing real usage and user need.

### MVP capabilities

#### 1. Accounts and privacy

- Secure registration and login, account recovery, session logout, and account deletion.
- Each user can access only their own portfolios; data isolation must be testable at both the API and database layers.
- Clearly explain consent, data use, retention, and how users can request an export or deletion.

#### 2. Portfolio and transaction ledger

- Create one or more portfolios with an explicit market and reporting currency.
- Record opening balances, buys, sells, fees, deposits, withdrawals, and cash reconciliation.
- Import CSV using a published format, with preview, row-level errors, and protection against unintended duplicates.
- The file contract is documented in [Transaction CSV Format](Transaction_CSV_Format.md).
- View and export transaction history; correct records through auditable events rather than silent overwrites.

#### 3. Prices and data quality

- Show each asset's price, source, retrieval time, and whether it is fresh or stale.
- On a refresh failure, retain the last valid price and show a warning; never label a stale price as live.
- Store the version and source of historical data, timezone, currency, and corporate-action adjustment method.
- Select a market benchmark only after confirming a reliable and permitted source for the index and adjusted history.

#### 4. Dashboard and reports

- Report securities and cash separately in rial; never add different currencies together.
- Show cost basis, realized and unrealized P/L, portfolio return, and asset allocation.
- Show performance over a selected period, drawdown, volatility, and concentration, with a short definition and data window for each metric.
- Compare with a market index over the overlapping period and make the difference between benchmark and portfolio clear.
- Provide CSV export and a readable report for personal records.
- Periodic returns must account for external cash flows. Until time-weighted return is complete and validated, any simple return must be labeled precisely and its limits explained.

#### 5. Explainability and user control

- Show how each total, weight, P/L figure, and metric was derived from trades and prices.
- Warn about incomplete data, incomplete cash history, stale prices, unknown units, and insufficient periods.
- Never execute a trade or change a portfolio without an explicit user action.

### Out of scope for the first release

- Placing buy/sell orders, holding user funds or assets, transferring money, or connecting to a trading account.
- Personalized buy/sell advice, automatic recommendations, or discretionary portfolio management.
- US markets, FX conversion, and combining multi-currency assets into one figure.
- Real-time trading, social features, copy trading, paid signals, leverage, and derivatives.
- Funds and alternative assets until their data and event accounting are reliable.
- An AI assistant that provides personalized investment advice.

These features are not permanently prohibited technically; each requires separate product, data, security, and, where applicable, licensing validation.

### Private-beta acceptance criteria

The beta is ready for a limited invitation only when:

1. Manual entry and CSV import reconcile against an independent ledger for sample buys, sells, fees, and cash flows.
2. All financial reports show the currency and latest quote time, and never present a failed quote as fresh.
3. Calculation tests cover fees, stock splits, cash dividends, returns with cash flows, market holidays, and missing data.
4. Cross-account isolation tests prove a user cannot read or change another user's data.
5. Backup and restore, sensitive-event logging, account deletion, and data export have been exercised.
6. Data-source rights, privacy notice, terms of use, product description, and regulated-service boundaries have been reviewed.
7. In a small beta, target users can create a portfolio, import data, and interpret the report without direct assistance; recurring problems are recorded and addressed.

### Commercial risks and launch gates

- **Licensing and service scope:** analytics, personalized suggestions, advice, portfolio management, and order execution may have different legal treatment. Before public or paid release, document the exact scope with legal counsel familiar with Iran's capital-market rules. Marketing text or a disclaimer does not replace this review.
- **Data rights:** technical access does not grant commercial redistribution rights. Review each provider's terms for display and storage.
- **Accuracy responsibility:** incorrect prices, corporate actions, or currency units can mislead users; every output must have traceable provenance and limits.
- **Security:** holdings and investment behavior are sensitive. Access control, encryption, secret management, backup, and incident response must be operational before beta.
- **Revenue hypothesis to validate:** free beta followed by subscription for reports and analysis. Transaction-based fees or asset management are outside the MVP.

### Delivery plan

#### Stage 0 — Product and scope validation

- Interview 5–10 target investors about their current record-keeping and reporting needs.
- Prepare sample CSV data from real activity with personal and account details removed.
- Conduct an initial review of data rights and legal boundaries.
- Confirm the first-release market and asset scope.

#### Stage 1 — Reliable core

- Stabilize transaction-ledger, cash, fee, and corporate-action accounting.
- Define time-weighted performance and benchmarks with data source and quality metadata.
- Complete import/export and stale/incomplete-data warnings.

#### Stage 2 — Multi-user web beta

- Production API and database, secure login, user isolation, and audit events.
- Responsive web interface for the MVP workflows.
- Limited deployment with monitoring, backup, recovery, and feedback collection.

#### Stage 3 — Commercial readiness

- Complete legal and data-provider review, privacy, terms, support, and incident-response processes.
- Measure activation, repeated use, data errors, and willingness to pay.
- Decide on subscription, native apps, official brokerage connectivity, or more asset classes only from beta evidence.

### Assumptions and decisions to confirm

This proposal assumes the initial user is a **self-directed individual investor in Iran** and the product is a **read-only personal analysis and management tool**. Open decisions include:

- Is the target user the self-directed investor, or an adviser/financial team?
- Are equities and cash sufficient initially, or must funds be included from day one?
- Is responsive web/PWA enough for beta, or is Android required at launch?
- Is the long-term goal an independent analytics product or official brokerage integration?

Initial recommendation: equities and cash, manual/CSV entry, responsive web, and no order placement. This scope is faster to validate and has lower operating risk.
