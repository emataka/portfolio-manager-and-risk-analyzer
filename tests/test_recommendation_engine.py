import pandas as pd

from core.recommendation.recommendation_engine import RecommendationEngine


class StaticMarketData:
    def __init__(self, histories):
        self.histories = histories

    def get_price_history(self, ticker, market):
        return self.histories[ticker]


class EqualWeight:
    def optimize(self, expected_returns, covariance_matrix):
        tickers = list(covariance_matrix.columns)
        return {ticker: 1 / len(tickers) for ticker in tickers}


def test_recommendation_uses_one_common_return_window_and_reports_its_dates():
    dates_a = pd.date_range("2025-01-01", periods=4)
    dates_b = pd.date_range("2025-01-02", periods=4)
    service = StaticMarketData(
        {
            "A": pd.Series([100.0, 110.0, 121.0, 132.0], index=dates_a),
            "B": pd.Series([100.0, 110.0, 99.0, 108.9], index=dates_b),
        }
    )
    engine = RecommendationEngine(service, EqualWeight(), risk_free_rate=0.05)

    result = engine.generate_recommendation(["A", "B"], "US", risk_aversion_coefficient=2.5)

    assert result["observation_count"] == 2
    assert result["history_start"] == dates_a[2]
    assert result["history_end"] == dates_a[3]
    assert result["portfolio_variance"] > 0
    assert "raw_risky_allocation" in result
