from cli.questionnaire_cli import run_questionnaire
from core.data.data_service import MarketDataService
from core.data.universe import get_screened_universe
from core.optimization.strategies.max_sharpe import MaxSharpeStrategy
from core.recommendation.recommendation_engine import RecommendationEngine

RISK_FREE_RATE = 0.05
MARKET = "US"

def main():
    print("به سیستم پیشنهاد سرمایه گذاری خوش اومدی!")
    print("\nلطفا به سوال های زیر جواب بده تا سطح ریسک گریزیت مشخص بشه.")
    
    TICKERS = get_screened_universe(tickers_per_sector=3)
    profile = run_questionnaire()
    print(f"\nدسته ریسک گریزی شما: {profile['category']}")
    
    market_data_service = MarketDataService()
    strategy = MaxSharpeStrategy(risk_free_rate=RISK_FREE_RATE)
    engine = RecommendationEngine(market_data_service, strategy, RISK_FREE_RATE)
    
    recommendation = engine.generate_recommendation(
        TICKERS, MARKET, profile["risk_aversion_coefficient"]
    )
    print_recommendation(recommendation)

def print_recommendation(recommendation):
    print("\nهشدار: این ارقام از داده‌های تاریخی محاسبه شده‌اند؛ پیش‌بینی بازده آینده یا توصیه مالی نیستند.")
    print(
        f"بازه داده: {recommendation['history_start']:%Y-%m-%d} تا "
        f"{recommendation['history_end']:%Y-%m-%d} "
        f"({recommendation['observation_count']} بازده روزانه مشترک)"
    )

    for ticker, weight in recommendation["weights"].items():
        if weight > 0.001:
            print(f"  {ticker}: {weight:.1%}")
    
    print()
    print(f"میانگین تاریخی بازده سالانه (نه پیش‌بینی): {recommendation['portfolio_return']:.1%}")
    print(f"نوسان تاریخی سالانه: {recommendation['portfolio_variance'] ** 0.5:.1%}")
    print()
    raw_allocation = recommendation["raw_risky_allocation"]
    if raw_allocation > 1:
        print(
            f"هشدار: فرمول سادهٔ تخصیص، سهم پرریسک خام {raw_allocation:.1%} را به دست داده "
            "و برنامه آن را به سقف 100% محدود کرده است. این نتیجه به برآوردهای تاریخی حساس است."
        )
    elif raw_allocation < 0:
        print(
            f"فرمول سادهٔ تخصیص، سهم پرریسک خام {raw_allocation:.1%} را به دست داده "
            "و برنامه آن را به کف 0% محدود کرده است."
        )
    risky = recommendation["risky_allocation"]
    print(f"خروجی فرمول تخصیص: {risky:.1%} برای این ترکیب پرریسک")
    print(f"{1 - risky:.1%} در دارایی بدون ریسک")

if __name__ == "__main__":
    main()
