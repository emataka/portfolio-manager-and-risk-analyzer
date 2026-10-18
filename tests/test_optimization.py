from types import SimpleNamespace

import numpy as np
import pandas as pd
import pytest

from core.optimization.strategies.max_sharpe import MaxSharpeStrategy
from core.optimization.strategies.min_variance import MinVarianceStrategy


@pytest.fixture
def covariance_matrix():
    return pd.DataFrame(
        [[0.04, 0.01], [0.01, 0.09]],
        index=["A", "B"],
        columns=["A", "B"],
    )


@pytest.mark.parametrize(
    "strategy",
    [MinVarianceStrategy(), MaxSharpeStrategy(risk_free_rate=0.02)],
)
def test_optimizers_return_finite_long_only_weights_summing_to_one(strategy, covariance_matrix):
    weights = strategy.optimize({"A": 0.08, "B": 0.12}, covariance_matrix)

    assert set(weights) == {"A", "B"}
    assert all(np.isfinite(weight) and 0 <= weight <= 1 for weight in weights.values())
    assert sum(weights.values()) == pytest.approx(1.0)


def test_optimizer_rejects_non_finite_covariance(covariance_matrix):
    covariance_matrix.loc["A", "A"] = np.nan

    with pytest.raises(ValueError, match="finite"):
        MinVarianceStrategy().optimize({"A": 0.08, "B": 0.12}, covariance_matrix)


def test_max_sharpe_fails_closed_when_solver_does_not_converge(monkeypatch, covariance_matrix):
    import core.optimization.strategies.max_sharpe as max_sharpe_module

    monkeypatch.setattr(
        max_sharpe_module,
        "minimize",
        lambda *args, **kwargs: SimpleNamespace(
            success=False,
            x=np.array([0.5, 0.5]),
            message="synthetic failure",
        ),
    )

    with pytest.raises(RuntimeError, match="synthetic failure"):
        MaxSharpeStrategy().optimize({"A": 0.08, "B": 0.12}, covariance_matrix)
