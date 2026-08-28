"""
Unit Tests for ONNX Model Exporter and ONNX High-Performance Inference Engine.
"""

import os
import json
import pytest
import numpy as np
import onnx

from aoe2_coach.models.feature_encoder import FeatureEncoder, FEATURE_NAMES
from aoe2_coach.models.strategy_classifier import StrategyClassifier, COMPOSITION_CLASSES
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES
from aoe2_coach.models.onnx_exporter import ONNXExporter
from aoe2_coach.models.onnx_inference import ONNXInferenceEngine


def test_onnx_export_and_inference_end_to_end(tmp_path):
    encoder = FeatureEncoder()
    n_samples = 30
    X = np.random.randn(n_samples, encoder.num_features).astype(np.float32)

    # 1. Train models
    strat_clf = StrategyClassifier()
    strat_clf.fit(X, np.random.choice(COMPOSITION_CLASSES, size=n_samples).tolist())

    win_est = WinProbabilityEstimator()
    win_est.fit(X, np.random.choice([0, 1], size=n_samples))

    eco_reb = EconomicRebalancer()
    eco_reb.fit(X, np.random.dirichlet(np.ones(4), size=n_samples).astype(np.float32))

    stance_pred = StanceTimingPredictor()
    stance_pred.fit(X, np.random.choice(STANCE_CLASSES, size=n_samples).tolist())

    # 2. Export to ONNX
    artifacts_dir = str(tmp_path / "artifacts")
    exporter = ONNXExporter(num_features=encoder.num_features)
    paths = exporter.export_all(
        strategy_classifier=strat_clf,
        win_estimator=win_est,
        economic_rebalancer=eco_reb,
        stance_predictor=stance_pred,
        artifacts_dir=artifacts_dir,
    )

    for name, path in paths.items():
        assert os.path.exists(path)
        if path.endswith(".onnx"):
            model = onnx.load(path)
            onnx.checker.check_model(model)

    # 3. Test ONNX Inference Session
    engine = ONNXInferenceEngine(artifacts_dir=artifacts_dir)
    assert engine.is_loaded

    test_x = np.random.randn(3, encoder.num_features).astype(np.float32)

    strat_probs = engine.predict_strategy_proba(test_x)
    assert strat_probs.shape == (3, len(COMPOSITION_CLASSES))

    win_probs = engine.predict_win_probability(test_x)
    assert win_probs.shape == (3,)
    assert (win_probs >= 0.0).all() and (win_probs <= 1.0).all()

    eco_ratios = engine.predict_economic_ratios(test_x)
    assert eco_ratios.shape == (3, 4)
    assert np.allclose(eco_ratios.sum(axis=1), 1.0)

    stance_probs = engine.predict_stance_proba(test_x)
    assert stance_probs.shape == (3, len(STANCE_CLASSES))
