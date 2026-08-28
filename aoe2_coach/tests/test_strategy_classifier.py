"""
Unit Tests for Strategy Classifier Model.
"""

import os
import pytest
import numpy as np

from aoe2_coach.models.strategy_classifier import (
    StrategyClassifier,
    COMPOSITION_CLASSES,
    map_label_to_canonical_comp,
    StrategyPrediction,
)
from aoe2_coach.models.feature_encoder import FeatureEncoder


def test_map_label_to_canonical_comp():
    assert map_label_to_canonical_comp("knight") == "knight_line"
    assert map_label_to_canonical_comp("paladin") == "knight_line"
    assert map_label_to_canonical_comp("crossbowman") == "crossbow_line"
    assert map_label_to_canonical_comp("pikeman") == "pike_line"
    assert map_label_to_canonical_comp("skirmisher") == "skirm_line"
    assert map_label_to_canonical_comp("camel_rider") == "camel_line"
    assert map_label_to_canonical_comp("mangonel") == "siege_line"
    assert map_label_to_canonical_comp("monk") == "monk_line"
    assert map_label_to_canonical_comp("berserk") == "unique_unit_line"
    assert map_label_to_canonical_comp("champion") == "champion_line"


def test_strategy_classifier_train_and_predict(tmp_path):
    encoder = FeatureEncoder()
    clf = StrategyClassifier()

    # Synthetic training data
    n_samples = 40
    X = np.random.randn(n_samples, encoder.num_features).astype(np.float32)
    y = np.random.choice(COMPOSITION_CLASSES, size=n_samples).tolist()

    clf.fit(X, y)
    assert clf.is_trained

    # Predict proba
    probs = clf.predict_proba(X[:5])
    assert probs.shape == (5, len(COMPOSITION_CLASSES))
    assert np.allclose(probs.sum(axis=1), 1.0)

    # Predict single
    sample_state = {"player_civ": "Franks", "opponent_civ": "Vikings", "player_age": 3}
    pred = clf.predict_single(sample_state)
    assert isinstance(pred, StrategyPrediction)
    assert pred.primary_composition in COMPOSITION_CLASSES
    assert 0.0 <= pred.confidence <= 1.0
    assert len(pred.rankings) == len(COMPOSITION_CLASSES)
    assert pred.recommended_building in ["stable", "archery_range", "barracks", "siege_workshop", "monastery", "castle", "town_center"]

    # Save & Load test
    save_path = os.path.join(tmp_path, "strat_test.joblib")
    clf.save(save_path)
    assert os.path.exists(save_path)

    loaded_clf = StrategyClassifier()
    loaded_clf.load(save_path)
    assert loaded_clf.is_trained
    loaded_pred = loaded_clf.predict_single(sample_state)
    assert loaded_pred.primary_composition == pred.primary_composition
