"""
AoE2 Coach Machine Learning Module.
Provides Strategy Classifier, Win Probability Estimator, Economic Rebalancer,
Stance & Timing Predictor, ONNX Exporter, and unified MLInferenceService.
"""

from aoe2_coach.models.feature_encoder import (
    FeatureEncoder,
    FEATURE_NAMES,
    CIV_ARCHETYPES,
    UNIT_CATEGORY_MAP,
)
from aoe2_coach.models.strategy_classifier import (
    StrategyClassifier,
    StrategyPrediction,
    CompositionRanking,
    COMPOSITION_CLASSES,
    BUILDING_CLASSES,
    TECH_CLASSES,
)
from aoe2_coach.models.win_probability_estimator import (
    WinProbabilityEstimator,
    WinProbabilityResult,
    classify_advantage_level,
)
from aoe2_coach.models.economic_rebalancer import (
    EconomicRebalancer,
    MacroRebalancePlan,
    HIGH_ELO_RATIOS,
)
from aoe2_coach.models.stance_timing_predictor import (
    StanceTimingPredictor,
    StanceTimingResult,
    STANCE_CLASSES,
)
from aoe2_coach.models.onnx_exporter import ONNXExporter
from aoe2_coach.models.onnx_inference import ONNXInferenceEngine
from aoe2_coach.models.inference_service import (
    MLInferenceService,
    MLRecommendation,
    MatchContext,
)

__all__ = [
    "FeatureEncoder",
    "FEATURE_NAMES",
    "CIV_ARCHETYPES",
    "UNIT_CATEGORY_MAP",
    "StrategyClassifier",
    "StrategyPrediction",
    "CompositionRanking",
    "COMPOSITION_CLASSES",
    "BUILDING_CLASSES",
    "TECH_CLASSES",
    "WinProbabilityEstimator",
    "WinProbabilityResult",
    "classify_advantage_level",
    "EconomicRebalancer",
    "MacroRebalancePlan",
    "HIGH_ELO_RATIOS",
    "StanceTimingPredictor",
    "StanceTimingResult",
    "STANCE_CLASSES",
    "ONNXExporter",
    "ONNXInferenceEngine",
    "MLInferenceService",
    "MLRecommendation",
    "MatchContext",
]
