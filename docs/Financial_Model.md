# Financial model and calculation conventions

This document records the prototype's current calculation conventions. It is not a claim that live provider data or portfolio recommendations have been independently validated.

## Price data and returns

- Inputs are positive price observations indexed by dates. Calculations do not fill missing prices.
- Portfolio-level calculations align assets on common dates. A date with a missing value for any selected asset is excluded from the aligned panel.
- Simple daily return is `P[t] / P[t-1] - 1`.
- The annualization factor is 252 trading days. Expected return is the arithmetic mean of daily returns multiplied by 252; volatility is sample standard deviation multiplied by `sqrt(252)`.
- Covariance is estimated from aligned daily returns and multiplied by 252.
- Portfolio assets store an explicit quote currency: `USD` for the US provider and `IRR` for the Tehran provider. Portfolio reports aggregate values, cost basis, P/L, and concentration weights by currency, and scalar total methods reject mixed-currency portfolios. No FX conversion is performed. `pytse-client` exposes the TSETMC last-trade value as a raw numeric quote; the project treats it as rial, consistent with TSETMC sourced price displays (for example, [Tindex's وبملت history](https://tindex.app/stocks/%D9%88%D8%A8%D9%85%D9%84%D8%AA/history/)). Any manual purchase price must use the same unit. Toman values must be converted to rial before entry (1 toman = 10 rial).
- Portfolio market value includes same-currency cash. Buy costs (including fees) reduce cash, sell proceeds (after fees) increase cash, and explicit opening cash/deposit/withdrawal/reconciliation events are recorded in the ledger. Cash and securities are never combined across currencies. Imported opening security balances do not imply a cash flow. Older snapshots lack opening cash history and must be reconciled against the current broker balance before their total value is relied on. A negative cash balance indicates missing funding history or spending beyond recorded cash; it is not a margin recommendation.
- Time-weighted return (TWR) removes the effect of external deposits and withdrawals by calculating returns between valuations around each external flow and geometrically linking the sub-period returns. The most accurate calculation needs a reliable portfolio valuation at the start, at the end, and immediately before each external cash flow; the flow is then included in the next sub-period's beginning value. Internal income, fees, and trades remain part of investment performance. See the [GIPS calculation methodology guidance](https://www.gipsstandards.org/wp-content/uploads/2021/03/calculation_methodology_gs_2011.pdf). The core calculator requires these valuation points and does not infer or fetch historical prices. The read-only portfolio API now reports TWR from active, non-voided valuation points. It reports `insufficient_data` when fewer than two active observations exist or the latest observation has an external flow after it; calculation failures are `unavailable` with a warning. The reported percentage is total return over the recorded period, not annualized.
- The transaction ledger supports `OPENING_BALANCE`, `BUY`, and `SELL`. Buys add gross cost and fees to basis; sells realize proceeds less fees minus the weighted-average basis of shares sold. Remaining holdings retain weighted-average unit cost. Unrealized P/L is securities value less remaining basis; total P/L adds realized P/L. `UNREALIZED RETURN` divides unrealized P/L by remaining securities basis. `CUMULATIVE RETURN ON NET CONTRIBUTIONS` divides total P/L by net external contributions (opening security balances at recorded basis, opening cash, deposits, withdrawals, and cash reconciliations). It is a simple, non-annualized ratio and does not account for contribution timing; it is not time-weighted return or money-weighted IRR. This figure is omitted when cash history is incomplete or net contributions are not positive.
- Transactions are append-only and must be entered in chronological order. Legacy snapshots become opening balances at migration time; they cannot recover prior trades, realized P/L, fees, or dates.
- If a live price update fails, the asset retains its last saved price. The CLI marks that holding as not updated and prints the provider error. Totals that include it are therefore based on a stale quote and need manual review.
- US live quotes are requested with `auto_adjust=False`; historical US close prices used for analysis/backtesting are requested with `auto_adjust=True`, so Yahoo/yfinance's adjusted OHLC series accounts for splits and dividends. The Iran provider's adjustment status and full data provenance are not yet encoded; verify its corporate-action treatment before relying on long-horizon results.
- The US universe currently comes from today's S&P 500 constituents. The optimizer and reported historical estimates use the same data window, so the result has survivor and in-sample selection bias and must not be treated as a forward forecast.

## Allocation

For an estimated risky portfolio with annual return `mu`, variance `sigma_squared`, risk-aversion coefficient `gamma`, and annual risk-free rate `rf`, the prototype computes:

```text
y = (mu - rf) / (gamma * sigma_squared)
```

The risky share is clipped to `[0, 1]`, so this model does not borrow or short. `gamma` and variance must be positive. This is a simplified mean-variance rule; estimates from historical data are uncertain and the questionnaire-to-gamma mapping needs its own validation.

All rates passed to allocation and performance functions are decimals per year (for example, `0.05` means 5%).

## Backtesting

- At each rebalance, estimates use the configured lookback window ending before the rebalance date. The rebalance-date close is used to value the execution.
- Rebalance turnover is calculated from actual pre-trade weights after price drift. The value series records the post-cost portfolio value on the execution date; observations do not carry the pre-trade value across a rebalance boundary.
- The first reported value is the initial capital in cash on the last warm-up observation. The first rebalance happens on the next observation, so entry costs are included in measured performance. Metrics describe the out-of-sample portion only.
- Weights must be long-only, between zero and one, and sum to one.
- Transaction cost is applied to the full sum of absolute weight changes times portfolio value. The configured rate should match that convention.
- The risk-free allocation is compounded at an equivalent daily rate over observed trading rows.
- The CLI compares the strategy with both a 100%-invested, buy-and-hold SPY benchmark and an SPY/cash benchmark with the same risky allocation over the same observations. The latter uses the strategy's recommended risky allocation in SPY and compounds the remainder at the configured risk-free rate; it matches the allocation, not realized volatility or total risk. The 100%-invested SPY result remains a broad-market reference. Current S&P 500 constituents still create survivorship bias in the strategy universe.

These are simplified assumptions. The engine does not currently model bid/ask spread, market impact, taxes, partial fills, cash flows, delisted assets, or market-specific calendars.

## Performance metrics

- Total return uses first and last portfolio values.
- Annualized return compounds total return over `(observation_count - 1) / 252` years.
- Annualized volatility uses sample standard deviation of observed daily portfolio returns and `sqrt(252)`.
- Sharpe ratio uses arithmetic daily excess returns: `mean(daily_return - daily_risk_free_return) / sample_std(daily_return) * sqrt(252)`. The annual risk-free rate is converted to an equivalent daily rate; it must be finite and greater than `-100%`. Sharpe is undefined for a zero-volatility series.
- Maximum drawdown is the minimum decline from a previous running peak and is reported as a negative fraction.

## نسخهٔ فارسی

این سند قراردادهای محاسباتی فعلی نمونهٔ اولیه را ثبت می‌کند. وجود این قراردادها به معنی اعتبارسنجی مستقل دادهٔ زندهٔ provider یا پیشنهادهای پرتفوی نیست.

### دادهٔ قیمت و بازده

- ورودی‌ها مشاهده‌های مثبت قیمت برحسب تاریخ هستند. محاسبات مقدارهای گمشده را پر نمی‌کنند.
- محاسبات سطح پرتفوی دارایی‌ها را روی تاریخ‌های مشترک هم‌تراز می‌کنند. اگر در یک تاریخ دادهٔ هر دارایی انتخاب‌شده ناقص باشد، آن تاریخ از پنل هم‌تراز حذف می‌شود.
- بازده سادهٔ روزانه برابر است با `P[t] / P[t-1] - 1`.
- ضریب سالانه‌سازی ۲۵۲ روز معاملاتی است. بازده مورد انتظار از میانگین حسابی بازده روزانه ضرب‌در ۲۵۲ و نوسان از انحراف معیار نمونه ضرب‌در `sqrt(252)` محاسبه می‌شود.
- کوواریانس از بازده‌های روزانهٔ هم‌تراز برآورد و در ۲۵۲ ضرب می‌شود.
- دارایی‌ها ارز مظنهٔ صریح دارند: `USD` برای provider آمریکا و `IRR` برای provider تهران. گزارش‌ها ارزش، بهای تمام‌شده، سودوزیان و وزن تمرکز را به تفکیک ارز جمع می‌کنند؛ متدهای جمع کل از پرتفوی چندارزی خودداری می‌کنند و تبدیل ارز انجام نمی‌شود. `pytse-client` مقدار خام عددی آخرین معاملهٔ TSETMC را می‌دهد و پروژه آن را ریال در نظر می‌گیرد، مطابق نمایش قیمت‌های مبتنی بر TSETMC (برای نمونه [تاریخچهٔ وبملت در Tindex](https://tindex.app/stocks/%D9%88%D8%A8%D9%85%D9%84%D8%AA/history/)). قیمت خرید دستی باید با همان واحد وارد شود. مبلغ تومانی پیش از ورود باید به ریال تبدیل شود (هر تومان = ۱۰ ریال).
- ارزش بازار پرتفوی وجه نقد همان ارز را شامل می‌شود. هزینهٔ خرید با کارمزد از نقد کم و دریافتی فروش پس از کارمزد به نقد اضافه می‌شود؛ رویدادهای وجه نقد آغازین، واریز، برداشت و تطبیق نیز ثبت می‌شوند. وجه نقد و اوراق از ارزهای متفاوت با هم جمع نمی‌شوند. موجودی آغازین اوراق واردشده به معنی جریان نقدی نیست. snapshotهای قدیمی سابقهٔ وجه نقد آغازین ندارند و پیش از اتکا به ارزش کل باید با ماندهٔ فعلی کارگزاری تطبیق داده شوند. ماندهٔ نقد منفی می‌تواند نشان‌دهندهٔ سرمایهٔ اولیهٔ ثبت‌نشده یا خرید فراتر از نقد ثبت‌شده باشد؛ توصیهٔ استفاده از اعتبار نیست.
- بازده زمان‌وزن (TWR) اثر واریز و برداشت خارجی را با محاسبهٔ بازده بین ارزش‌گذاری‌های اطراف هر جریان و پیوند هندسی بازده‌های زیردوره حذف می‌کند. دقیق‌ترین محاسبه به ارزش‌گذاری معتبر در آغاز، پایان و بلافاصله پیش از هر جریان خارجی نیاز دارد؛ جریان پس از ارزش‌گذاری به سرمایهٔ آغاز زیردورهٔ بعد افزوده می‌شود. درآمد داخلی، کارمزد و معامله بخشی از عملکرد سرمایه‌گذاری هستند. [راهنمای روش محاسبهٔ GIPS](https://www.gipsstandards.org/wp-content/uploads/2021/03/calculation_methodology_gs_2011.pdf) را ببین. هستهٔ محاسباتی این نقاط را لازم دارد و قیمت تاریخی را حدس نمی‌زند یا واکشی نمی‌کند. API فقط‌خواندنی TWR را از نقاط فعال و باطل‌نشده گزارش می‌کند. با کمتر از دو مشاهدهٔ فعال یا وجود جریان خارجی پس از آخرین مشاهده، وضعیت `insufficient_data` است؛ خطای محاسباتی وضعیت `unavailable` و هشدار دارد. درصد بازگشتی، بازده کل دورهٔ ثبت‌شده است و سالانه نمی‌شود.
- دفتر معامله از `OPENING_BALANCE`، `BUY` و `SELL` پشتیبانی می‌کند. خرید، بهای ناخالص و کارمزد را به بهای تمام‌شده اضافه می‌کند؛ فروش سود تحقق‌یافته را به‌صورت دریافتی پس از کارمزد منهای بهای میانگین موزون سهام فروخته‌شده محاسبه می‌کند. دارایی باقی‌مانده بهای واحد میانگین موزون را حفظ می‌کند. سودوزیان تحقق‌نیافته برابر ارزش اوراق منهای بهای باقیمانده است و سودوزیان کل، سود تحقق‌یافته را نیز می‌افزاید. `UNREALIZED RETURN` سود تحقق‌نیافته را بر بهای اوراق باقیمانده تقسیم می‌کند. `CUMULATIVE RETURN ON NET CONTRIBUTIONS` سودوزیان کل را بر آوردهٔ خالص بیرونی تقسیم می‌کند (موجودی آغازین اوراق به بهای ثبت‌شده، نقد آغازین، واریز، برداشت و تعدیل تطبیق نقد). این نسبت ساده و غیرسالانه‌سازی‌شده است و زمان‌بندی واریزها را لحاظ نمی‌کند؛ TWR یا IRR پولی نیست. اگر تاریخچهٔ نقد ناقص یا آوردهٔ خالص نامثبت باشد، نمایش داده نمی‌شود.
- معامله‌ها append-only هستند و باید به ترتیب زمانی ثبت شوند. snapshot قدیمی هنگام مهاجرت به موجودی آغازین تبدیل می‌شود و نمی‌تواند معاملات قبلی، سود تحقق‌یافته، کارمزدها یا تاریخ‌ها را بازسازی کند.
- اگر دریافت قیمت زنده شکست بخورد، دارایی آخرین قیمت ذخیره‌شده را نگه می‌دارد. CLI آن را به‌روزرسانی‌نشده علامت می‌زند و خطای provider را چاپ می‌کند. بنابراین جمعی که آن قیمت را دارد بر پایهٔ مظنهٔ قدیمی است و باید دستی بازبینی شود.
- مظنهٔ زندهٔ آمریکا با `auto_adjust=False` دریافت می‌شود؛ قیمت پایانی تاریخی آمریکا برای تحلیل و بک‌تست با `auto_adjust=True` درخواست می‌شود تا سری تعدیل‌شدهٔ OHLC در Yahoo/yfinance تقسیم سهم و سود نقدی را لحاظ کند. وضعیت تعدیل provider ایران و منشأ کامل داده هنوز در مدل ثبت نمی‌شود؛ پیش از اتکا به نتایج بلندمدت، نحوهٔ اعمال رویدادهای شرکتی را بررسی کن.
- جهان سهام آمریکا از اعضای فعلی S&P 500 ساخته می‌شود. optimizer و برآورد تاریخی روی یک پنجرهٔ داده کار می‌کنند؛ بنابراین سوگیری بقا و برازش درون‌نمونه کنترل نشده و نتیجه پیش‌بینی آینده نیست.

### تخصیص سرمایه

برای پرتفوی پرریسک با بازده سالانهٔ برآوردی `mu`، واریانس `sigma_squared`، ضریب ریسک‌گریزی `gamma` و نرخ سالانهٔ بدون ریسک `rf`، نمونه محاسبه می‌کند:

```text
y = (mu - rf) / (gamma * sigma_squared)
```

سهم پرریسک به بازهٔ `[0, 1]` محدود می‌شود؛ بنابراین مدل وام‌گیری یا فروش استقراضی ندارد. `gamma` و واریانس باید مثبت باشند. این قاعدهٔ سادهٔ میانگین-واریانس است؛ برآوردهای تاریخی نامطمئن‌اند و نگاشت پرسش‌نامه به gamma باید جداگانه اعتبارسنجی شود.

نرخ‌های ورودی به توابع تخصیص و عملکرد، اعشاری و سالانه هستند؛ مثلاً `0.05` یعنی ۵٪.

### بک‌تست

- در هر بازتوازن، برآوردها از پنجرهٔ نگاه‌به‌عقب استفاده می‌کنند که پیش از تاریخ بازتوازن تمام می‌شود. قیمت پایانی تاریخ بازتوازن برای ارزش‌گذاری اجرا استفاده می‌شود.
- گردش معاملات با وزن‌های واقعی پیش از معامله و پس از تغییر قیمت محاسبه می‌شود. سری ارزش، ارزش پرتفوی پس از هزینه را در روز اجرا ثبت می‌کند؛ مشاهده‌ها ارزش پیش از بازتوازن را از مرز اجرا عبور نمی‌دهند.
- نخستین ارزش گزارش‌شده، سرمایهٔ اولیه به‌صورت نقد در آخرین مشاهدهٔ دورهٔ warm-up است. نخستین بازتوازن در مشاهدهٔ بعدی رخ می‌دهد، بنابراین هزینهٔ ورود در عملکرد سنجیده‌شده لحاظ می‌شود. معیارها فقط بخش out-of-sample را توصیف می‌کنند.
- وزن‌ها باید long-only، بین صفر و یک و جمعشان برابر یک باشد.
- هزینهٔ معامله روی مجموع قدرمطلق تغییر وزن‌ها ضرب‌در ارزش پرتفوی اعمال می‌شود. نرخ پیکربندی‌شده باید با همین قرارداد سازگار باشد.
- تخصیص بدون ریسک با نرخ روزانهٔ معادل در ردیف‌های معاملاتی مشاهده‌شده مرکب می‌شود.
- CLI استراتژی را هم با معیار SPY صددرصد سرمایه‌گذاری‌شده و نگهداری بلندمدت و هم با معیار SPY/نقد با تخصیص پرریسک همسان در همان مشاهدات مقایسه می‌کند. معیار دوم سهم پرریسک پیشنهادی استراتژی را در SPY می‌گذارد و بقیه را با نرخ بدون ریسک مرکب می‌کند؛ تخصیص را همسان می‌کند، نه نوسان تحقق‌یافته یا کل ریسک را. SPY صددرصدی یک مرجع کلی بازار است. استفاده از اعضای فعلی S&P 500 همچنان سوگیری بقا ایجاد می‌کند.

این‌ها فرض‌های ساده‌شده هستند. موتور فعلاً فاصلهٔ bid/ask، اثر بازار، مالیات، اجرای ناقص، جریان نقدی، دارایی حذف‌شده از بازار و تقویم‌های اختصاصی بازار را مدل نمی‌کند.

### معیارهای عملکرد

- بازده کل از اولین و آخرین مقدار پرتفوی محاسبه می‌شود.
- بازده سالانه‌سازی‌شده، بازده کل را روی `(observation_count - 1) / 252` سال مرکب می‌کند.
- نوسان سالانه‌سازی‌شده از انحراف معیار نمونهٔ بازده روزانهٔ مشاهده‌شده ضرب‌در `sqrt(252)` به دست می‌آید.
- نسبت شارپ از بازده مازاد روزانهٔ حسابی استفاده می‌کند: `mean(daily_return - daily_risk_free_return) / sample_std(daily_return) * sqrt(252)`. نرخ سالانهٔ بدون ریسک به نرخ روزانهٔ معادل تبدیل می‌شود و باید متناهی و بیشتر از `-100%` باشد. برای سری با نوسان صفر، شارپ تعریف‌نشده است.
- حداکثر افت، کمترین کاهش از یک اوج قبلی است و به‌صورت کسری منفی گزارش می‌شود.
