# تاریخچهٔ ارزش‌گذاری / Valuation History

## فارسی

این مرحله ذخیرهٔ نقاط ارزش‌گذاری زمان‌دار در SQLite و ورود دستی آن‌ها از CLI را فراهم می‌کند. این داده‌ها برای محاسبهٔ بازده وزنی زمان (TWR) استفاده می‌شوند؛ ارزش‌گذاری‌ها خودکار نیستند و منبع قیمت به کارگزاری وصل نشده است.

هر نقطه شامل این موارد است:

- شناسهٔ پرتفوی و ارز (`USD` یا `IRR`)
- زمان ارزش‌گذاری؛ در پایگاه داده به UTC تبدیل می‌شود
- ارزش کل پرتفوی به همان ارز
- جریان نقدی خارجی بلافاصله پس از ارزش‌گذاری؛ واریز مثبت و برداشت منفی است
- منبع ثبت (برای نمونه، صورت‌حساب کارگزاری یا تطبیق دستی)
- شمارهٔ ترتیبی و زمان ثبت در سیستم

منبع و تاریخ ارزش‌گذاری دو مفهوم جدا هستند. زمان ثبت سیستم نیز برای ردگیری زمان ورود داده نگهداری می‌شود. نقاط هر پرتفوی و ارز به‌ترتیب زمانی افزوده می‌شوند و قابل ویرایش یا حذف نیستند. برای دادهٔ آزمایشی یا اشتباه، گزینهٔ ابطال یک رکورد اصلاحی append-only با دلیل و زمان ثبت می‌کند؛ رکورد اصلی باقی می‌ماند اما در TWR نادیده گرفته می‌شود. ابطال هم قابل ویرایش یا حذف نیست.

### اعمال مهاجرت پایگاه داده

از پوشهٔ پروژه اجرا کنید:

```powershell
py -3.14 -m api.migrate_db
```

این فرمان مسیر `PORTFOLIO_API_DB` را می‌خواند و اگر تنظیم نشده باشد از `data/portfolio.sqlite3` استفاده می‌کند. فرمان فقط schema را به‌روز می‌کند و دادهٔ JSON وارد نمی‌کند. اگر مسیر پایگاه دادهٔ دیگری دارید:

```powershell
py -3.14 -m api.migrate_db --database "مسیر\portfolio.sqlite3"
```

پیش از مهاجرت پایگاه دادهٔ شخصی، نسخهٔ پشتیبان بگیرید. مهاجرت جدول خالی ارزش‌گذاری‌ها را ایجاد می‌کند و هیچ ارزش تاریخی را حدس نمی‌زند یا تولید نمی‌کند.

### ثبت ارزش‌گذاری و مشاهدهٔ TWR

پس از واردبودن پرتفوی در SQLite و اجرای مهاجرت بالا، از پوشهٔ پروژه اجرا کنید:

```powershell
py -3.14 -m cli.valuation_cli
```

فرمان از `PORTFOLIO_API_DB` و `PORTFOLIO_API_PORTFOLIO_ID` استفاده می‌کند؛ پیش‌فرض آن‌ها `data/portfolio.sqlite3` و `local` است. هنگام ثبت، ارزش کل همان ارز را با وجه نقد وارد کنید. جریان خارجی را فقط وقتی ثبت کنید که بلافاصله بعد از زمان ارزش‌گذاری رخ می‌دهد؛ واریز مثبت و برداشت منفی است. برای محاسبهٔ TWR باید ارزش‌گذاری قبل از هر جریان خارجی، ارزش‌گذاری بعد از آن، و نقاط آغاز و پایان بازه وجود داشته باشند. نقطهٔ آخر نباید جریان خارجی بعد از خود داشته باشد.

برای کنارگذاشتن رکورد آزمایشی/اشتباه، گزینهٔ ۳ را انتخاب کنید، ارز و شمارهٔ رکورد را بدهید، دلیل را وارد کنید و در تأیید عبارت `VOID` را بنویسید. این کار رکورد اصلی را پاک نمی‌کند؛ اصلاح در تاریخچه دیده می‌شود و مقدار باطل‌شده از محاسبهٔ TWR کنار می‌رود. از این گزینه فقط برای دادهٔ نادرست استفاده کنید، نه برای اصلاح عادی ارزش پرتفوی.

در `GET /api/v1/portfolio` خلاصهٔ عملکرد به تفکیک ارز برمی‌گردد. `total_return_percentage` بازده کل در دورهٔ ثبت‌شده است و سالانه‌سازی نمی‌شود. اگر کمتر از دو نقطهٔ فعال وجود داشته باشد یا آخرین نقطه هنوز جریان خارجی بعد از خود داشته باشد، وضعیت `insufficient_data` است؛ خطاهای محاسباتی با وضعیت `unavailable` و هشدار برمی‌گردند.

### محدودیت‌های فعلی

- ثبت دستی از CLI و repository پایتون انجام می‌شود؛ مسیر HTTP نوشتنی یا دریافت خودکار قیمت ایجاد نشده است.
- مبالغ ارزهای مختلف با هم جمع نمی‌شوند و تبدیل ارز انجام نمی‌شود.
- ارزش‌گذاری و جریان نقدی باید از منبع مورد اعتماد وارد شوند؛ دادهٔ بازار خودکار در این مرحله وارد نشده است.
- TWR فقط وقتی قابل اتکاست که نقاط آغاز، پایان و نقاط لازم اطراف جریان‌های خارجی ثبت شده باشند.

## English

This stage adds SQLite storage and manual CLI entry for timestamped valuation points. These observations support time-weighted return (TWR); valuations are not captured automatically and no broker price source is connected. Append-only void records can exclude test or incorrect observations while retaining the original and the correction reason in the audit history.

Each observation stores:

- Portfolio identifier and currency (`USD` or `IRR`)
- Valuation timestamp, normalized to UTC in the database
- Total portfolio value in that currency
- External cash flow immediately after the valuation; deposits are positive and withdrawals are negative
- Recording source, such as a broker statement or manual reconciliation
- Sequence number and system creation timestamp

The valuation timestamp and the source are distinct pieces of provenance. The system creation timestamp records when the observation entered the database. Points are appended in chronological order for each portfolio and currency and cannot be updated or deleted. Test or incorrect observations can be excluded with an append-only void marker that records its reason and timestamp; the original row remains in the audit history.

### Apply the database migration

Run from the project directory:

```powershell
py -3.14 -m api.migrate_db
```

The command uses `PORTFOLIO_API_DB`, or `data/portfolio.sqlite3` when that variable is unset. It upgrades the schema only and does not import JSON data. To select another database file:

```powershell
py -3.14 -m api.migrate_db --database "path\to\portfolio.sqlite3"
```

Back up a personal database before migration. The migration creates an empty valuation table; it does not infer or fabricate historical values.

### Record valuations and view TWR

After the portfolio has been imported into SQLite and the migration above has run, start the CLI from the project directory:

```powershell
py -3.14 -m cli.valuation_cli
```

The command reads `PORTFOLIO_API_DB` and `PORTFOLIO_API_PORTFOLIO_ID`, defaulting to `data/portfolio.sqlite3` and `local`. Enter the total value in the selected currency, including cash. Record an external flow only when it occurs immediately after the valuation timestamp; deposits are positive and withdrawals are negative. TWR requires valuations before each external flow, after those flows, and at the beginning and end of the period. The final point must have no flow after it.

To exclude a test or incorrect record, choose option 3, select the currency and sequence number, enter a reason, and confirm with `VOID`. This does not delete the original point; the correction remains visible in history and the voided point is excluded from TWR. Use this only for invalid data, not for ordinary portfolio updates.

`GET /api/v1/portfolio` returns a performance summary per currency. `total_return_percentage` is the total return over the recorded period and is not annualized. If fewer than two active points exist or the latest point still has an external flow after it, the status is `insufficient_data`; calculation failures return `unavailable` with a warning.

### Current limits

- Manual values are entered through the CLI and Python repository; no HTTP write route or automatic quote capture is exposed.
- Different currencies are not added together and no currency conversion is performed.
- Valuations and cash flows must come from a trusted source; automated market data is not part of this stage.
- TWR is reliable only when the required beginning, ending, and external-flow valuation points are present.

The read-only portfolio API includes a per-currency `performance` summary. `total_return_percentage` is the non-annualized return for the stored period. The status is `insufficient_data` when fewer than two active observations exist or the latest observation still has a flow after it; calculation errors are reported as `unavailable` with a warning. Voided points are excluded from the calculation and counted separately.
