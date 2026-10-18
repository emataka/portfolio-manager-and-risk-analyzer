import pandas as pd

from cli.questionnaire_cli import run_questionnaire
from core.backtesting.backtest_engine import (
    run_allocated_backtest,
    run_buy_and_hold_backtest,
)
from core.backtesting.performance_metrics import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_total_return,
)
from core.data.data_service import MarketDataService
from core.data.universe import get_screened_universe
from core.optimization.strategies.max_sharpe import MaxSharpeStrategy
from core.recommendation.recommendation_engine import RecommendationEngine

RISK_FREE_RATE = 0.05
MARKET = "US"
BACKTEST_YEARS = 3
BENCHMARK_TICKER = "SPY"
INITIAL_CAPITAL = 10000


def main():
    print("به بخش بک تست خوش اومدی!")
    print("\nداریم بررسی میکنیم اگه این پیشنهاد رو رو داده تاریخی دنبال میکردی، چی میشد.\n")

    TICKERS = get_screened_universe(tickers_per_sector=3)
    profile = run_questionnaire()
    print(f"\nدسته ریسک گریزی شما: {profile['category']}")

    market_data_service = MarketDataService()
    strategy = MaxSharpeStrategy(risk_free_rate=RISK_FREE_RATE)
    engine = RecommendationEngine(market_data_service, strategy, RISK_FREE_RATE)

    recommendation = engine.generate_recommendation(
        TICKERS, MARKET, profile["risk_aversion_coefficient"]
    )

    price_histories = {
        ticker: market_data_service.get_price_history(ticker, MARKET, years=BACKTEST_YEARS)
        for ticker in TICKERS
    }

    result = run_allocated_backtest(
        strategy,
        price_histories,
        risky_allocation=recommendation["risky_allocation"],
        risk_free_rate=RISK_FREE_RATE,
        initial_capital=INITIAL_CAPITAL,
    )
    benchmark_history = market_data_service.get_price_history(
        BENCHMARK_TICKER, MARKET, years=BACKTEST_YEARS
    )
    benchmark_history = benchmark_history.reindex(result.index).dropna()
    result = result.loc[benchmark_history.index]
    benchmark = run_buy_and_hold_backtest(
        {BENCHMARK_TICKER: 1.0},
        {BENCHMARK_TICKER: benchmark_history},
        initial_capital=INITIAL_CAPITAL,
    )
    allocation_matched_benchmark = _run_allocation_matched_spy_backtest(
        benchmark_history,
        risky_allocation=recommendation["risky_allocation"],
        risk_free_rate=RISK_FREE_RATE,
        initial_capital=INITIAL_CAPITAL,
    )
    print_backtest_result(
        result,
        benchmark,
        allocation_matched_benchmark=allocation_matched_benchmark,
        risky_allocation=recommendation["risky_allocation"],
    )


def _run_allocation_matched_spy_backtest(
    price_history, *, risky_allocation, risk_free_rate, initial_capital
):
    dates = price_history.index
    daily_risk_free_rate = (1 + risk_free_rate) ** (1 / 252) - 1
    risk_free_value = pd.Series(
        [
            initial_capital * (1 - risky_allocation)
            * (1 + daily_risk_free_rate) ** day
            for day in range(len(dates))
        ],
        index=dates,
    )
    if risky_allocation == 0:
        return risk_free_value

    risky_value = run_buy_and_hold_backtest(
        {BENCHMARK_TICKER: 1.0},
        {BENCHMARK_TICKER: price_history},
        initial_capital=initial_capital * risky_allocation,
    )
    return risky_value + risk_free_value


def print_backtest_result(
    result, benchmark=None, *, allocation_matched_benchmark=None, risky_allocation=None
):
    series = {"strategy": result}
    if benchmark is not None:
        series["benchmark"] = benchmark
    if allocation_matched_benchmark is not None:
        series["allocation_matched_benchmark"] = allocation_matched_benchmark

    if len(series) > 1:
        aligned = pd.concat(series, axis=1, join="inner").dropna()
        if len(aligned) < 2:
            raise ValueError("Strategy and benchmark need at least two common observations.")
        series = {name: aligned[name] for name in aligned.columns}

    print("عملکرد استراتژی پیشنهادی:")
    _print_metrics(series["strategy"])

    if benchmark is not None:
        print(
            f"\nمعیار مرجع: {BENCHMARK_TICKER}، نگهداری و سرمایه‌گذاری ۱۰۰٪ "
            "(تعدیل‌شده بابت تقسیم و سود نقدی؛ با ریسک استراتژی هم‌تراز نیست)"
        )
        _print_metrics(series["benchmark"])
        return_gap = calculate_total_return(series["strategy"]) - calculate_total_return(
            series["benchmark"]
        )
        cagr_gap = calculate_annualized_return(series["strategy"]) - calculate_annualized_return(
            series["benchmark"]
        )
        print(f"\nتفاوت بازده کل استراتژی با SPY: {return_gap:+.1%} (واحد درصد)")
        print(f"تفاوت بازده سالانه با SPY: {cagr_gap:+.1%} (واحد درصد)")

    if allocation_matched_benchmark is not None:
        label = "SPY و وجه نقد با تخصیص پرریسک یکسان"
        if risky_allocation is not None:
            label += f" ({risky_allocation:.1%} در SPY؛ باقی‌مانده با نرخ بدون‌ریسک)"
        print(f"\nمعیار مرجع با تخصیص مشابه: {label}")
        _print_metrics(series["allocation_matched_benchmark"])
        return_gap = calculate_total_return(series["strategy"]) - calculate_total_return(
            series["allocation_matched_benchmark"]
        )
        cagr_gap = calculate_annualized_return(series["strategy"]) - calculate_annualized_return(
            series["allocation_matched_benchmark"]
        )
        print(f"\nتفاوت بازده کل استراتژی با معیار تخصیص مشابه: {return_gap:+.1%} (واحد درصد)")
        print(f"تفاوت بازده سالانه با معیار تخصیص مشابه: {cagr_gap:+.1%} (واحد درصد)")


def _print_metrics(values):
    print(f"بازده کل: {calculate_total_return(values):.1%}")
    print(f"بازده سالانه: {calculate_annualized_return(values):.1%}")
    print(f"ریسک سالانه: {calculate_annualized_volatility(values):.1%}")
    print(f"نسبت شارپ: {calculate_sharpe_ratio(values, RISK_FREE_RATE):.2f}")
    print(f"حداکثر افت: {calculate_max_drawdown(values):.1%}")


if __name__ == "__main__":
    main()
