from cli.questionnaire_cli import run_questionnaire
from core.data.data_service import MarketDataService
from core.optimization.strategies.max_sharpe import MaxSharpeStrategy
from core.recommendation.recommendation_engine import RecommendationEngine

RISK_FREE_RATE = 0.05
TICKERS = ["AAPL", "TSLA", "NVDA"]
MARKET = "US"

def main():
    print("به سیستم پیشنهاد سرمایه گذاری خوش اومدی!")
    print("\nلطفا به سوال های زیر جواب بده تا سطح ریسک گریزیت مشخص بشه.")
    
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
    for ticker, weight in recommendation["weights"].items():
        print(f"  {ticker}: {weight:.1%}")
    
    print()
    print(f"بازده مورد انتظار: {recommendation['portfolio_return']:.1%}")
    print(f"ریسک: {recommendation['portfolio_variance'] ** 0.5:.1%}")
    print()
    risky = recommendation["risky_allocation"]
    print(f"{risky:.1%} از سرمایه بره تو این ترکیب")
    print(f"{1 - risky:.1%} تو دارایی بدون ریسک بمونه")

if __name__ == "__main__":
    main()
