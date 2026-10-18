# Portfolio Manager & Risk Analyzer

A dual-market (US & Iran) portfolio management and investment recommendation engine, built in Python. Given a user's risk tolerance, it recommends an optimal asset allocation, manages a live portfolio, and backtests the recommended strategy against historical data.

> **Project Status:** 🚧 Prototype under active development. End-to-end flows are implemented, while financial assumptions, data quality, and backtesting behavior are still being hardened. Outputs are for learning and decision support, not investment advice.

---

## Overview

This project started as a simple portfolio tracker and evolved into a full investment recommendation engine, modeled loosely on the "smart recommendation" features of apps like Mofid App, but scoped as a personal decision-support tool rather than a licensed brokerage.

Given a set of tickers and a user's answers to a short risk-tolerance questionnaire, the engine:

1. Fetches historical price data (US equities via `yfinance`, Iranian equities via `pytse-client`)
2. Computes historical annualized mean return, volatility, and a covariance matrix for the chosen assets
3. Runs one of several portfolio optimization strategies (equal-weight, minimum variance, maximum Sharpe ratio) to find the optimal risky portfolio
4. Applies the investor's risk-aversion coefficient to decide what share of capital should go into that risky portfolio versus a risk-free asset (two-fund separation theorem)
5. Can backtest the resulting strategy against historical data, including periodic rebalancing and transaction costs

The project is also a hands-on learning exercise in Python, object-oriented design, and quantitative finance.

---

## Features

- **Dual-market data layer** — a shared `MarketDataProvider` interface with US (`yfinance`) and Iran (`pytse-client`) implementations, so the rest of the system never needs to know which market an asset belongs to
- **Asset & Portfolio models** — validated, encapsulated domain objects (properties/setters, duplicate-asset protection)
- **Currency-aware portfolio reports** — US quotes are denominated in USD and Tehran market quotes in IRR; cash and securities are valued by currency without implicit FX conversion, and failed quote refreshes are flagged as stale
- **Risk-aversion questionnaire** — a scored questionnaire mapping answers to a risk-aversion coefficient and category (conservative / moderate / risk-tolerant / aggressive)
- **Risk & return analytics** — historical annualized mean return, volatility, and covariance matrix from historical prices
- **Pluggable optimization strategies** — equal-weight, minimum variance, and maximum Sharpe ratio, each implementing a shared `OptimizationStrategy` interface (built with `scipy.optimize`); more strategies (risk parity, hierarchical risk parity, mean-CVaR) are planned
- **Capital allocation** — splits capital between the optimal risky portfolio and a risk-free asset based on the user's risk aversion
- **Recommendation engine** — orchestrates the full pipeline (data → analytics → optimization → allocation) into a single recommendation
- **Backtesting engine** — buy-and-hold and periodic-rebalancing simulations with transaction costs, plus performance metrics (CAGR, volatility, Sharpe ratio, maximum drawdown)
- **Portfolio persistence** — versioned JSON save/load for holdings and saved prices, with explicit overwrite confirmation in the CLI
- **Transaction ledger** — append-only position and cash events with timestamps, fees, weighted-average cost basis, currency-specific cash balances, cash reconciliation, and realized/unrealized P/L and cumulative return
- **Valuation history and TWR** — timestamped, currency-specific valuations with source provenance, append-only void corrections, and time-weighted performance in the local API report
- **Local SQLite API** — read-only portfolio and transaction views; a development prototype without authentication or user isolation
- **Unified CLI** — a single menu (`cli/app.py`) for portfolio management, recommendations, and backtesting
- **Automated tests** — `pytest` coverage for models, transaction accounting, analytics, backtesting, allocation, optimization, providers, and persistence

---

## Architecture

The codebase is split into two layers:

- **`core/`** — pure business logic (data, analytics, optimization, profiling, recommendation, backtesting). Contains no printing or user-interaction code, so it can be reused by any future client (CLI, web, mobile, API) without modification.
- **`cli/`** — the only client today. All `input()`/`print()` calls live here; `core/` is completely UI-agnostic.

Extensibility is built around abstract base classes: adding a new market (e.g. gold, currency) means writing one new `MarketDataProvider` subclass; adding a new optimization approach means writing one new `OptimizationStrategy` subclass. Nothing else in the system needs to change.

---

## Technologies

- Python 3.12 (the version targeted by continuous integration)
- [yfinance](https://pypi.org/project/yfinance/) — US market data
- [pytse-client](https://pypi.org/project/pytse-client/) — Iran (Tehran Stock Exchange) market data
- pandas / NumPy — data handling and numerical computation
- SciPy (`scipy.optimize`) — constrained portfolio optimization
- pytest — automated testing

Planned: risk parity / hierarchical risk parity / mean-CVaR strategies, additional asset classes and FX conversion, and a multi-user API/web client after authentication and data isolation are implemented.

---

## Project Structure

```text
portfolio-manager-and-risk-analyzer/
│
├── core/                       # Platform-independent business logic
│   ├── models/                 # Asset and Portfolio domain models
│   ├── data/
│   │   └── providers/          # Pluggable market data providers (US, Iran)
│   ├── analytics/              # Risk & return calculations
│   ├── profiling/              # Risk-aversion questionnaire & scoring
│   ├── optimization/
│   │   └── strategies/         # Pluggable optimization strategies
│   ├── recommendation/         # Combines profile + optimization into a recommendation
│   ├── backtesting/            # Historical simulation & performance metrics
│   └── persistence/            # Versioned portfolio and transaction storage
│
├── cli/                        # Command-line client
│   ├── app.py                  # Unified menu (entry point)
│   ├── main.py                 # Portfolio management
│   ├── recommend.py            # Investment recommendation
│   ├── backtest_cli.py         # Backtesting
│   └── questionnaire_cli.py    # Shared risk questionnaire flow
│
├── tests/                      # pytest suite
├── api/                        # Local FastAPI prototype and SQLite migrations
├── docs/                       # Architecture & design notes (work in progress)
│
├── requirements.txt
└── README.md
```

---

## Installation

```bash
git clone https://github.com/emataka/portfolio-manager-and-risk-analyzer.git
cd portfolio-manager-and-risk-analyzer
pip install -r requirements.txt
```

**Troubleshooting (`pytse-client` on Python 3.14):** `pytse-client` pins an old version of `lxml` that has no pre-built wheel for very new Python versions, which can trigger a "Microsoft Visual C++ 14.0 or greater is required" build error. If that happens:

```bash
pip install lxml
pip install pytse-client --no-deps
pip install aiohttp beautifulsoup4 black jdatetime pandas requests tenacity
```

---

## Usage

Run the unified CLI from the project root:

```bash
python -m cli.app
```

This opens a menu to manage a portfolio, get an investment recommendation, or backtest a strategy. Each feature can also be run standalone, e.g. `python -m cli.recommend`.

In the unified menu, choose option 4 to save or load a portfolio snapshot, option 5 to use the transaction ledger, and option 6 to exit. Option 5 lets you enter opening balances, buys, sells, and view the append-only transaction history. Enter transactions in chronological order; use the quote currency shown for the selected market. The default save file is `portfolio.json` in the current working directory. The CLI asks before overwriting an existing file.

Run the test suite:

```bash
python -m pytest
```

Tests use local, synthetic price histories and should not require live market data. The GitHub Actions workflow runs the suite on Python 3.12.

Record and review manual portfolio valuations in the local SQLite database with `python -m cli.valuation_cli`. The database must already contain the portfolio and have current migrations. See [Valuation History](docs/Valuation_History.md) for data conventions and TWR limitations.

### Local read-only API prototype

The optional FastAPI layer exposes a locally imported portfolio to a web client. After installing the project's base requirements, install the API/database dependencies and import a saved JSON portfolio. The API has no authentication and must stay bound to `127.0.0.1`:

```powershell
py -3.14 -m pip install -r requirements-web.txt
$env:PORTFOLIO_API_FILE = (Resolve-Path .\portfolio.json).Path
$env:PORTFOLIO_API_DB = (Join-Path (Get-Location) 'data\portfolio.sqlite3')
py -3.14 -m api.migrate_json
py -3.14 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for the API schema. The configured JSON file must already exist. See [Local API prototype](docs/API_Local_Prototype.md) for endpoint details and limitations. This is a development bridge to a future web client, not a multi-user or production service.

## Financial conventions and limitations

- Daily returns are annualized with 252 trading days.
- Backtest signals use prices before the rebalance date; orders are valued at the rebalance date's close.
- Price histories are aligned to dates shared by all selected assets. Missing observations are not forward-filled.
- US and Iranian assets use explicit USD and IRR quote currencies. The current model does not convert currencies or reconcile different trading calendars. Legacy schema v1 portfolio snapshots load with a currency inferred from their market; review their stored purchase-price units before relying on P/L.
- The US universe is sampled from today's S&P 500 constituents and the optimizer is fit on the same historical window used to calculate its output; survivor and in-sample bias are not controlled.
- Confirm the provider's dividend and split adjustment behavior before interpreting historical results.
- See [Financial Model](docs/Financial_Model.md) for formulas and [Development Guide](docs/Development_Guide.md) for local checks.
- See [Product MVP](docs/Product_MVP.md) for the proposed target user, launch market, first-release scope, and commercialization gates.
- See [Architecture](docs/Architecture.md) and [Roadmap](docs/Roadmap.md) for the proposed implementation structure and milestones.
- See [Transaction CSV format](docs/Transaction_CSV_Format.md) for the ledger import/export template.

---

## Roadmap

### Done
- [x] Dual-market data layer (US & Iran)
- [x] Asset / Portfolio models with validation
- [x] Risk-aversion questionnaire & profiling
- [x] Risk & return analytics, covariance matrix
- [x] Optimization strategies: equal-weight, minimum variance, maximum Sharpe
- [x] Capital allocation (two-fund separation)
- [x] End-to-end recommendation engine
- [x] Backtesting: buy-and-hold, periodic rebalancing, transaction costs
- [x] Performance metrics: CAGR, volatility, Sharpe ratio, max drawdown
- [x] Unified CLI menu
- [x] Initial pytest suite (models)

### In progress / planned
- [ ] Additional optimization strategies: risk parity, hierarchical risk parity, mean-CVaR
- [ ] Gold and currency markets
- [ ] Connecting capital allocation to the backtesting engine
- [x] Synthetic tests for analytics, backtesting, optimization, providers, and persistence
- [x] Offline validation of optimizer behavior and market data adapters
- [x] Persistence layer (saving/loading portfolios)
- [x] Local read-only API prototype for a future web client
- [ ] Multi-user API and responsive web client

---

## Learning Objectives

This project doubles as a hands-on learning exercise in:

- Python & Object-Oriented Programming
- Software architecture (separation of concerns, dependency inversion via abstract base classes, the strategy pattern)
- Quantitative finance (Modern Portfolio Theory, the Sharpe ratio, the two-fund separation theorem)
- Numerical optimization (`scipy.optimize`)
- Automated testing (`pytest`)
- Git & GitHub workflow

---

## Author

**Emataka**

GitHub: https://github.com/emataka

## نسخهٔ فارسی

# مدیریت پرتفوی و تحلیل ریسک

موتور مدیریت پرتفوی و پیشنهاد سرمایه‌گذاری برای بازارهای آمریکا و ایران که با Python ساخته شده است. بر اساس پاسخ‌های کاربر به پرسش‌نامهٔ ریسک، ترکیب دارایی پیشنهاد می‌دهد، پرتفوی را نگه‌داری می‌کند و راهبرد را روی دادهٔ تاریخی بک‌تست می‌کند.

> **وضعیت پروژه:** نمونهٔ اولیه در حال توسعه است. مسیرهای اصلی پیاده‌سازی شده‌اند، اما فرض‌های مالی، کیفیت داده و رفتار بک‌تست همچنان در حال تقویت‌اند. خروجی‌ها برای یادگیری و پشتیبانی تصمیم‌اند و توصیهٔ سرمایه‌گذاری محسوب نمی‌شوند.

## نمای کلی

پروژه از یک ثبت‌کنندهٔ سادهٔ پرتفوی به موتور پیشنهاد سرمایه‌گذاری گسترش یافته است؛ هدف، ابزار مستقل مدیریت و تحلیل است، نه کارگزاری مجاز یا مدیر سرمایه.

موتور با دریافت نمادها و پاسخ‌های پرسش‌نامه:

1. دادهٔ تاریخی قیمت را از `yfinance` برای سهام آمریکا و `pytse-client` برای سهام ایران دریافت می‌کند.
2. میانگین بازده سالانه، نوسان و ماتریس کوواریانس را از دادهٔ تاریخی محاسبه می‌کند.
3. یکی از راهبردهای بهینه‌سازی وزن مساوی، کمینه‌سازی واریانس یا بیشینه‌سازی شارپ را اجرا می‌کند.
4. با استفاده از ریسک‌گریزی سرمایه‌گذار، سهم سرمایهٔ پرریسک و دارایی بدون ریسک را تعیین می‌کند.
5. می‌تواند راهبرد را با بازتوازن دوره‌ای و هزینهٔ معامله روی دادهٔ تاریخی بک‌تست کند.

این پروژه تمرینی عملی برای Python، طراحی شیءگرا و مالی کمی نیز هست.

## قابلیت‌ها

- لایهٔ دادهٔ دو بازاری با رابط مشترک provider برای آمریکا و ایران.
- مدل‌های اعتبارسنجی‌شدهٔ دارایی و پرتفوی و جلوگیری از دارایی تکراری.
- گزارش آگاه از ارز: مظنهٔ آمریکا به USD و تهران به IRR است؛ تبدیل خودکار ارز انجام نمی‌شود و قیمت به‌روزنشده علامت می‌خورد.
- پرسش‌نامهٔ امتیازدهی ریسک و تحلیل تاریخی بازده، نوسان و کوواریانس.
- راهبردهای بهینه‌سازی قابل‌افزودن، تخصیص سرمایه و موتور پیشنهاد.
- بک‌تست خریدونگهداری و بازتوازن دوره‌ای همراه هزینه و معیارهای عملکرد.
- ذخیره/بارگذاری نسخه‌دار JSON، دفتر معاملات و وجه نقد append-only، بهای تمام‌شدهٔ میانگین موزون، تطبیق نقد، سودوزیان تحقق‌یافته و تحقق‌نیافته.
- تاریخچهٔ ارزش‌گذاری زمان‌دار به تفکیک ارز، ثبت منبع، اصلاحات ابطالیِ قابل‌ردیابی و TWR در گزارش محلی.
- API محلی فقط‌خواندنی برای پرتفوی و معاملات؛ فعلاً بدون احراز هویت یا جداسازی کاربر.
- رابط خط فرمان یکپارچه و آزمون‌های خودکار pytest.

## معماری

- `core/` منطق مالی، داده، تحلیل، بهینه‌سازی و بک‌تست را بدون وابستگی به ورودی/خروجی CLI نگه می‌دارد.
- `cli/` رابط خط فرمان است؛ ورودی و چاپ کاربر در این لایه قرار دارد.
- `api/` نمونهٔ محلی FastAPI، repository و migrationهای SQLite را دارد.

افزودن بازار جدید با پیاده‌سازی provider و افزودن روش بهینه‌سازی با پیاده‌سازی strategy انجام می‌شود.

## فناوری‌ها

- Python؛ CI در حال حاضر با Python 3.12 اجرا می‌شود.
- `yfinance`، `pytse-client`، pandas، NumPy، SciPy و pytest.
- برای API محلی: FastAPI، SQLAlchemy، Alembic و Uvicorn.

راهبردهای risk parity، HRP و mean-CVaR، کلاس‌های دارایی و تبدیل ارز هنوز در برنامه‌اند.

## نصب

```powershell
py -3.14 -m pip install -r requirements.txt
```

اگر نصب `pytse-client` روی Python 3.14 به‌دلیل نبود wheel سازگار برای `lxml` با خطای Microsoft Visual C++ روبه‌رو شد، ابتدا `lxml` را جدا نصب کن و سپس `pytse-client` را بدون وابستگی‌هایش نصب کن:

```powershell
py -3.14 -m pip install lxml
py -3.14 -m pip install pytse-client --no-deps
py -3.14 -m pip install aiohttp beautifulsoup4 black jdatetime pandas requests tenacity
```

## استفاده

از ریشهٔ پروژه اجرا کن:

```powershell
py -3.14 -m cli.app
```

منوی یکپارچه مدیریت پرتفوی، پیشنهاد، بک‌تست، ذخیره/بارگذاری و دفتر معاملات را ارائه می‌کند. معامله‌ها را به ترتیب زمان و با واحد پول نشان‌داده‌شده برای بازار ثبت کن. فایل پیش‌فرض `portfolio.json` در پوشهٔ فعلی است و CLI پیش از بازنویسی تأیید می‌گیرد.

برای ثبت دستی ارزش‌گذاری‌ها و مشاهدهٔ تاریخچه و TWR از SQLite:

```powershell
py -3.14 -m cli.valuation_cli
```

پایگاه داده باید از قبل پرتفوی را داشته و migrationهای جاری روی آن اجرا شده باشند. برای محدودیت‌ها و روش ثبت جریان خارجی، [تاریخچهٔ ارزش‌گذاری](docs/Valuation_History.md) را بخوان.

آزمون‌ها:

```powershell
py -3.14 -m pytest -q
```

آزمون‌ها از دادهٔ مصنوعی استفاده می‌کنند و نباید به دادهٔ زندهٔ بازار وابسته باشند. GitHub Actions با Python 3.12 آن‌ها را اجرا می‌کند.

### نمونهٔ API محلی فقط‌خواندنی

پس از نصب وابستگی‌های API و import یک فایل JSON ذخیره‌شده، API را فقط روی loopback اجرا کن:

```powershell
py -3.14 -m pip install -r requirements-web.txt
$env:PORTFOLIO_API_FILE = (Resolve-Path .\portfolio.json).Path
$env:PORTFOLIO_API_DB = (Join-Path (Get-Location) 'data\portfolio.sqlite3')
py -3.14 -m api.migrate_json
py -3.14 -m uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

مستندات API در `http://127.0.0.1:8000/docs` است. این API نمونهٔ توسعه است، احراز هویت یا پشتیبانی چندکاربره ندارد و برای انتشار عمومی آماده نیست. جزئیات در [نمونهٔ محلی API](docs/API_Local_Prototype.md) آمده است.

## قراردادهای مالی و محدودیت‌ها

- بازده روزانه با ۲۵۲ روز معاملاتی سالانه‌سازی می‌شود.
- سیگنال بک‌تست از قیمت‌های پیش از تاریخ بازتوازن استفاده می‌کند؛ سفارش با قیمت پایانی روز بازتوازن ارزش‌گذاری می‌شود.
- تاریخچهٔ قیمت روی تاریخ‌های مشترک دارایی‌ها هم‌تراز می‌شود؛ دادهٔ گمشده forward-fill نمی‌شود.
- بازار آمریکا و ایران ارزهای USD و IRR دارند؛ تبدیل ارز و تفاوت تقویم معاملاتی حل نشده است. snapshotهای legacy واحد ارز را از بازار استنباط می‌کنند و پیش از اتکا به سودوزیان باید قیمت خرید بررسی شود.
- جهان سهام آمریکا از اعضای فعلی S&P 500 نمونه‌گیری می‌شود؛ سوگیری بقا و برازش درون‌نمونه کنترل نشده است.
- پیش از تفسیر دادهٔ تاریخی، رفتار تعدیل تقسیم سهم و سود نقدی provider را بررسی کن.
- فرمول‌ها در [مدل مالی](docs/Financial_Model.md)، کار توسعه در [راهنمای توسعه](docs/Development_Guide.md)، محدودهٔ محصول در [Product MVP](docs/Product_MVP.md)، و معماری و نقشهٔ راه در سندهای مرتبط آمده‌اند.
- قالب ورود و خروج دفتر معاملات در [قالب CSV دفتر معاملات](docs/Transaction_CSV_Format.md) مستند است.

## نقشهٔ راه

### انجام‌شده

- لایهٔ دادهٔ دو بازاری، مدل‌های دارایی/پرتفوی و پرسش‌نامهٔ ریسک.
- تحلیل ریسک و بازده، بهینه‌سازی و تخصیص سرمایه.
- موتور پیشنهاد، بک‌تست و معیارهای عملکرد.
- CLI یکپارچه، ذخیره‌سازی نسخه‌دار و مجموعهٔ آزمون.
- مهاجرت محلی SQLite و API فقط‌خواندنی.
- تاریخچهٔ ارزش‌گذاری و TWR در گزارش API.

### در حال انجام یا برنامه‌ریزی‌شده

- اعتبارسنجی مرجع مستقل برای سناریوهای مالی و کیفیت داده.
- رویدادهای شرکتی ایران و منبع قیمت مجاز و پایدار.
- راهبردهای risk parity، HRP و mean-CVaR و کلاس‌های دارایی دیگر.
- API چندکاربره و وب‌کلاینت واکنش‌گرا پس از تکمیل احراز هویت و جداسازی داده.

## هدف‌های یادگیری

Python و برنامه‌نویسی شیءگرا، معماری نرم‌افزار، نظریهٔ مدرن پرتفوی، نسبت شارپ، بهینه‌سازی عددی، آزمون خودکار و گردش کار Git/GitHub.

## پدیدآورنده

**Emataka** — [GitHub](https://github.com/emataka)
