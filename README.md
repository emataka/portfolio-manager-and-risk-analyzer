# Portfolio Manager & Risk Analyzer

A dual-market (US & Iran) portfolio management and investment recommendation engine, built in Python. Given a user's risk tolerance, it recommends an optimal asset allocation, manages a live portfolio, and backtests the recommended strategy against historical data.

> **Project Status:** 🚧 Actively developed — core engine is functional end-to-end; more optimization strategies and asset classes are in progress.

---

## Overview

This project started as a simple portfolio tracker and evolved into a full investment recommendation engine, modeled loosely on the "smart recommendation" features of apps like Mofid App, but scoped as a personal decision-support tool rather than a licensed brokerage.

Given a set of tickers and a user's answers to a short risk-tolerance questionnaire, the engine:

1. Fetches historical price data (US equities via `yfinance`, Iranian equities via `pytse-client`)
2. Computes expected return, volatility, and a covariance matrix for the chosen assets
3. Runs one of several portfolio optimization strategies (equal-weight, minimum variance, maximum Sharpe ratio) to find the optimal risky portfolio
4. Applies the investor's risk-aversion coefficient to decide what share of capital should go into that risky portfolio versus a risk-free asset (two-fund separation theorem)
5. Can backtest the resulting strategy against historical data, including periodic rebalancing and transaction costs

The project is also a hands-on learning exercise in Python, object-oriented design, and quantitative finance.

---

## Features

- **Dual-market data layer** — a shared `MarketDataProvider` interface with US (`yfinance`) and Iran (`pytse-client`) implementations, so the rest of the system never needs to know which market an asset belongs to
- **Asset & Portfolio models** — validated, encapsulated domain objects (properties/setters, duplicate-asset protection)
- **Risk-aversion questionnaire** — a scored questionnaire mapping answers to a risk-aversion coefficient and category (conservative / moderate / risk-tolerant / aggressive)
- **Risk & return analytics** — expected return, volatility, and annualized covariance matrix from historical prices
- **Pluggable optimization strategies** — equal-weight, minimum variance, and maximum Sharpe ratio, each implementing a shared `OptimizationStrategy` interface (built with `scipy.optimize`); more strategies (risk parity, hierarchical risk parity, mean-CVaR) are planned
- **Capital allocation** — splits capital between the optimal risky portfolio and a risk-free asset based on the user's risk aversion
- **Recommendation engine** — orchestrates the full pipeline (data → analytics → optimization → allocation) into a single recommendation
- **Backtesting engine** — buy-and-hold and periodic-rebalancing simulations with transaction costs, plus performance metrics (CAGR, volatility, Sharpe ratio, maximum drawdown)
- **Unified CLI** — a single menu (`cli/app.py`) for portfolio management, recommendations, and backtesting
- **Automated tests** — a growing `pytest` suite, currently covering the core models

---

## Architecture

The codebase is split into two layers:

- **`core/`** — pure business logic (data, analytics, optimization, profiling, recommendation, backtesting). Contains no printing or user-interaction code, so it can be reused by any future client (CLI, web, mobile, API) without modification.
- **`cli/`** — the only client today. All `input()`/`print()` calls live here; `core/` is completely UI-agnostic.

Extensibility is built around abstract base classes: adding a new market (e.g. gold, currency) means writing one new `MarketDataProvider` subclass; adding a new optimization approach means writing one new `OptimizationStrategy` subclass. Nothing else in the system needs to change.

---

## Technologies

- Python 3.14
- [yfinance](https://pypi.org/project/yfinance/) — US market data
- [pytse-client](https://pypi.org/project/pytse-client/) — Iran (Tehran Stock Exchange) market data
- pandas / NumPy — data handling and numerical computation
- SciPy (`scipy.optimize`) — constrained portfolio optimization
- pytest — automated testing

Planned: risk parity / hierarchical risk parity / mean-CVaR strategies, gold & currency markets, a persistence layer, and eventually a web/mobile API layer.

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
│   └── backtesting/            # Historical simulation & performance metrics
│
├── cli/                        # Command-line client
│   ├── app.py                  # Unified menu (entry point)
│   ├── main.py                 # Portfolio management
│   ├── recommend.py            # Investment recommendation
│   ├── backtest_cli.py         # Backtesting
│   └── questionnaire_cli.py    # Shared risk questionnaire flow
│
├── tests/                      # pytest suite
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

Run the test suite:

```bash
python -m pytest
```

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
- [ ] Expanded test coverage (data layer, optimization, backtesting)
- [ ] Persistence layer (saving/loading portfolios)
- [ ] Eventually: an API layer for web/mobile clients

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
