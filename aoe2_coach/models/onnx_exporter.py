"""
AoE2 ONNX Model Exporter:
Converts trained scikit-learn / LightGBM models into optimized Open Neural Network Exchange (.onnx) format.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
import numpy as np
import onnx
from skl2onnx import convert_sklearn
from skl2onnx.common.data_types import FloatTensorType

from aoe2_coach.models.feature_encoder import FEATURE_NAMES, FeatureEncoder
from aoe2_coach.models.strategy_classifier import StrategyClassifier, COMPOSITION_CLASSES
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES

logger = logging.getLogger(__name__)


class ONNXExporter:
    """
    Converts and packages all AoE2 Coach ML models into standardized ONNX binaries.
    """

    def __init__(self, num_features: int = len(FEATURE_NAMES)):
        self.num_features = num_features
        self.initial_type = [("float_input", FloatTensorType([None, self.num_features]))]

    def export_strategy_classifier(
        self, classifier: StrategyClassifier, output_path: str
    ) -> str:
        """Export StrategyClassifier to ONNX."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        onnx_model = convert_sklearn(
            classifier.comp_model,
            initial_types=self.initial_type,
            target_opset=17,
            options={type(classifier.comp_model): {"zipmap": False}},
        )
        onnx.checker.check_model(onnx_model)
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        logger.info(f"StrategyClassifier ONNX exported to {output_path}")
        return output_path

    def export_win_estimator(
        self, estimator: WinProbabilityEstimator, output_path: str
    ) -> str:
        """Export WinProbabilityEstimator to ONNX."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        onnx_model = convert_sklearn(
            estimator.model,
            initial_types=self.initial_type,
            target_opset=17,
            options={type(estimator.model): {"zipmap": False}},
        )
        onnx.checker.check_model(onnx_model)
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        logger.info(f"WinProbabilityEstimator ONNX exported to {output_path}")
        return output_path

    def export_economic_rebalancer(
        self, rebalancer: EconomicRebalancer, output_path: str
    ) -> str:
        """Export EconomicRebalancer to ONNX."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        onnx_model = convert_sklearn(
            rebalancer.model,
            initial_types=self.initial_type,
            target_opset=17,
        )
        onnx.checker.check_model(onnx_model)
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        logger.info(f"EconomicRebalancer ONNX exported to {output_path}")
        return output_path

    def export_stance_predictor(
        self, stance_pred: StanceTimingPredictor, output_path: str
    ) -> str:
        """Export StanceTimingPredictor to ONNX."""
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        onnx_model = convert_sklearn(
            stance_pred.model,
            initial_types=self.initial_type,
            target_opset=17,
            options={type(stance_pred.model): {"zipmap": False}},
        )
        onnx.checker.check_model(onnx_model)
        with open(output_path, "wb") as f:
            f.write(onnx_model.SerializeToString())
        logger.info(f"StanceTimingPredictor ONNX exported to {output_path}")
        return output_path

    def export_all(
        self,
        strategy_classifier: StrategyClassifier,
        win_estimator: WinProbabilityEstimator,
        economic_rebalancer: EconomicRebalancer,
        stance_predictor: StanceTimingPredictor,
        artifacts_dir: str = "aoe2_coach/models/artifacts",
    ) -> Dict[str, str]:
        """Export all models to ONNX and generate metadata JSON."""
        os.makedirs(artifacts_dir, exist_ok=True)

        paths = {
            "strategy_classifier": os.path.join(artifacts_dir, "strategy_classifier.onnx"),
            "win_estimator": os.path.join(artifacts_dir, "win_probability_estimator.onnx"),
            "economic_rebalancer": os.path.join(artifacts_dir, "economic_rebalancer.onnx"),
            "stance_predictor": os.path.join(artifacts_dir, "stance_predictor.onnx"),
            "metadata": os.path.join(artifacts_dir, "model_metadata.json"),
        }

        self.export_strategy_classifier(strategy_classifier, paths["strategy_classifier"])
        self.export_win_estimator(win_estimator, paths["win_estimator"])
        self.export_economic_rebalancer(economic_rebalancer, paths["economic_rebalancer"])
        self.export_stance_predictor(stance_predictor, paths["stance_predictor"])

        metadata = {
            "num_features": self.num_features,
            "feature_names": FEATURE_NAMES,
            "composition_classes": COMPOSITION_CLASSES,
            "stance_classes": STANCE_CLASSES,
            "opset_version": 17,
            "models": {
                "strategy_classifier": "strategy_classifier.onnx",
                "win_estimator": "win_probability_estimator.onnx",
                "economic_rebalancer": "economic_rebalancer.onnx",
                "stance_predictor": "stance_predictor.onnx",
            },
        }

        with open(paths["metadata"], "w") as f:
            json.dump(metadata, f, indent=2)

        return paths
