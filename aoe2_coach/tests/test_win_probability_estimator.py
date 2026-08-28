"""
Unit Tests for Win Probability Estimator (Value Model).
"""

import os
import pytest
import numpy as np

from aoe2_coach.models.win_probability_estimator import (
    WinProbabilityEstimator,
    WinProbabilityResult,
    classify_advantage_level,
)
from aoe2_coach.models.feature_encoder import FeatureEncoder


def test_classify_advantage_level():
    assert classify_advantage_level(0.90) == "dominant_lead"
    assert classify_advantage_level(0.75) == "moderate_lead"
    assert classify_advantage_level(0.58) == "slight_advantage"
    assert classify_advantage_level(0.50) == "even_match"
    assert classify_advantage_level(0.35) == "slight_disadvantage"
    assert classify_advantage_level(0.20) == "moderate_deficit"
    assert classify_advantage_level(0.08) == "critical_deficit"


def test_win_probability_estimator_train_and_evaluate(tmp_path):
    encoder = FeatureEncoder()
    estimator = WinProbabilityEstimator()

    # Generate training data
    n_samples = 50
    X = np.random.randn(n_samples, encoder.num_features).astype(np.float32)
    y = np.random.choice([0, 1], size=n_samples)

    estimator.fit(X, y)
    assert estimator.is_trained

    # Predict probabilities
    probs = estimator.predict_win_probability(X[:10])
    assert probs.shape == (10,)
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    # Evaluate single state
    sample_state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "vills_total": 50,
        "military_total": 20,
    }
    result = estimator.evaluate(sample_state)
    assert isinstance(result, WinProbabilityResult)
    assert 0.0 <= result.win_probability <= 1.0
    assert result.advantage_level in [
        "dominant_lead", "moderate_lead", "slight_advantage",
        "even_match", "slight_disadvantage", "moderate_deficit", "critical_deficit"
    ]
    assert len(result.key_win_factors) > 0

    # Save & Load
    save_path = os.path.join(tmp_path, "win_test.joblib")
    estimator.save(save_path)
    assert os.path.exists(save_path)

    loaded_est = WinProbabilityEstimator()
    loaded_est.load(save_path)
    assert loaded_est.is_trained
