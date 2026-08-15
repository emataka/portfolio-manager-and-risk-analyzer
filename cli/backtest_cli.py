from core.backtesting.backtest_engine import run_rebalancing_backtest
from core.backtesting.performance_metrics import (
    calculate_annualized_return,
    calculate_annualized_volatility,
    calculate_max_drawdown,
    calculate_sharpe_ratio,
    calculate_total_return,
)
from core.data.data_service import MarketDataService
from core.optimization.strategies.max_sharpe import MaxSharpeStrategy

RISK_FREE_RATE = 0.05
TICKERS = ["AAPL", "TSLA", "NVDA"]
MARKET = "US"
BACKTEST_YEARS = 3


def main():
    print("به بخش بک تست خوش اومدی!")
    print("\nداریم بررسی میکنیم اگه این استراتژی رو رو داده تاریخی دنبال میکردی، چی میشد.")
    
    market_data_service = MarketDataService()
    strategy = MaxSharpeStrategy(risk_free_rate=RISK_FREE_RATE)
    
    price_histories = {
        ticker: market_data_service.get_price_history(ticker, MARKET, years=BACKTEST_YEARS)
        for ticker in TICKERS
    }
    
    result = run_rebalancing_backtest(strategy, price_histories, initial_capital=10000)
    print_backtest_result(result)

def print_backtest_result(result):
    print(f"بازده کل: {calculate_total_return(result):.1%}")
    print(f"بازده سالانه: {calculate_annualized_return(result):.1%}")
    print(f"ریسک سالانه: {calculate_annualized_volatility(result):.1%}")
    print(f"نسبت شارپ: {calculate_sharpe_ratio(result, RISK_FREE_RATE):.2f}")
    print(f"حداکثر افت: {calculate_max_drawdown(result):.1%}")


if __name__ == "__main__":
    main()
