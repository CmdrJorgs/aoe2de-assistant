"""
Unit Tests for Stance & Timing Window Predictor.
"""

import os
import pytest
import numpy as np

from aoe2_coach.models.stance_timing_predictor import (
    StanceTimingPredictor,
    StanceTimingResult,
    STANCE_CLASSES,
)
from aoe2_coach.models.feature_encoder import FeatureEncoder


def test_stance_classes_defined():
    assert len(STANCE_CLASSES) == 5
    assert "ALL_IN_AGGRESSION" in STANCE_CLASSES
    assert "FORWARD_PRESSURE" in STANCE_CLASSES
    assert "DEFENSIVE_TURTLING" in STANCE_CLASSES


def test_stance_predictor_train_and_evaluate(tmp_path):
    encoder = FeatureEncoder()
    predictor = StanceTimingPredictor()

    n_samples = 40
    X = np.random.randn(n_samples, encoder.num_features).astype(np.float32)
    y = np.random.choice(STANCE_CLASSES, size=n_samples).tolist()

    predictor.fit(X, y)
    assert predictor.is_trained

    # Predict proba
    probs = predictor.predict_proba(X[:5])
    assert probs.shape == (5, len(STANCE_CLASSES))
    assert np.allclose(probs.sum(axis=1), 1.0)

    # Evaluate single state
    res = predictor.evaluate_timing_and_stance(
        state_or_vector=X[0],
        player_civ="Franks",
        opponent_civ="Vikings",
        player_age=3,
        game_time_sec=1300.0,
    )
    assert isinstance(res, StanceTimingResult)
    assert res.recommended_stance in STANCE_CLASSES
    assert 0.0 <= res.stance_confidence <= 1.0
    assert res.attack_window_sec > 0
    assert res.urgency in ["immediate", "medium", "steady", "defend_now"]
    assert len(res.civ_power_spike) > 0

    # Save & Load
    save_path = os.path.join(tmp_path, "stance_test.joblib")
    predictor.save(save_path)
    assert os.path.exists(save_path)

    loaded_pred = StanceTimingPredictor()
    loaded_pred.load(save_path)
    assert loaded_pred.is_trained
