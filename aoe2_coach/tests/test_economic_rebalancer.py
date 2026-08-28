"""
Unit Tests for Economic Rebalancer ML Model.
"""

import os
import pytest
import numpy as np

from aoe2_coach.models.economic_rebalancer import (
    EconomicRebalancer,
    MacroRebalancePlan,
    HIGH_ELO_RATIOS,
)
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.schemas.match import VillagerAllocation, ResourceStockpile


def test_high_elo_ratios_structure():
    assert "knight_line" in HIGH_ELO_RATIOS
    assert "crossbow_line" in HIGH_ELO_RATIOS
    for comp, ratios in HIGH_ELO_RATIOS.items():
        total_pct = sum(ratios.values())
        assert abs(total_pct - 1.0) < 1e-4


def test_economic_rebalancer_train_and_recommend(tmp_path):
    encoder = FeatureEncoder()
    rebalancer = EconomicRebalancer()

    # Generate synthetic training targets (N, 4)
    n_samples = 40
    X = np.random.randn(n_samples, encoder.num_features).astype(np.float32)
    Y_ratios = np.random.dirichlet(np.ones(4), size=n_samples).astype(np.float32)

    rebalancer.fit(X, Y_ratios)
    assert rebalancer.is_trained

    # Predict ratios
    preds = rebalancer.predict_ratios(X[:5])
    assert preds.shape == (5, 4)
    assert np.allclose(preds.sum(axis=1), 1.0)

    # Rebalance recommendation
    current_vills = VillagerAllocation(total=40, food=14, wood=20, gold=6, stone=0)
    current_stock = ResourceStockpile(food=150, wood=700, gold=100, stone=0)

    plan = rebalancer.recommend_rebalance(
        state_or_vector=X[0],
        current_vills=current_vills,
        current_stockpile=current_stock,
        strategy_comp="knight_line",
    )

    assert isinstance(plan, MacroRebalancePlan)
    assert plan.target_allocation.total == 40
    assert plan.target_allocation.food + plan.target_allocation.wood + plan.target_allocation.gold + plan.target_allocation.stone == 40
    assert "food" in plan.villager_shifts
    assert "wood" in plan.villager_shifts
    assert len(plan.shift_instructions) > 0
    assert plan.macro_health_grade in ["A", "B", "C", "D", "F"]

    # Save & Load
    save_path = os.path.join(tmp_path, "eco_test.joblib")
    rebalancer.save(save_path)
    assert os.path.exists(save_path)

    loaded_eco = EconomicRebalancer()
    loaded_eco.load(save_path)
    assert loaded_eco.is_trained
