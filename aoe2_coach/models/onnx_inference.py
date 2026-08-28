"""
AoE2 ONNX High-Performance Inference Engine:
Loads compiled ONNX models and executes sub-millisecond strategy & win rate inference.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np

try:
    import onnxruntime as ort
    HAS_ONNXRUNTIME = True
except ImportError:
    HAS_ONNXRUNTIME = False

from aoe2_coach.models.feature_encoder import FeatureEncoder, FEATURE_NAMES
from aoe2_coach.models.strategy_classifier import COMPOSITION_CLASSES
from aoe2_coach.models.stance_timing_predictor import STANCE_CLASSES

logger = logging.getLogger(__name__)


class ONNXInferenceEngine:
    """
    Ultra-low latency (<5ms) inference manager executing compiled ONNX binaries.
    """

    def __init__(self, artifacts_dir: str = "aoe2_coach/models/artifacts"):
        self.artifacts_dir = artifacts_dir
        self.encoder = FeatureEncoder()
        self.sessions: Dict[str, Any] = {}
        self.metadata: Dict[str, Any] = {}
        self.is_loaded = False

        if HAS_ONNXRUNTIME:
            self._init_sessions()

    def _init_sessions(self) -> None:
        """Initialize ONNX Runtime inference sessions with multi-threading."""
        meta_path = os.path.join(self.artifacts_dir, "model_metadata.json")
        if not os.path.exists(meta_path):
            logger.warning(f"ONNX metadata not found at {meta_path}. Fallback mode active.")
            return

        try:
            with open(meta_path, "r") as f:
                self.metadata = json.load(f)

            opts = ort.SessionOptions()
            opts.intra_op_num_threads = 2
            opts.graph_optimization_level = ort.GraphOptimizationLevel.ORT_ENABLE_ALL

            model_files = self.metadata.get("models", {})
            for key, filename in model_files.items():
                mpath = os.path.join(self.artifacts_dir, filename)
                if os.path.exists(mpath):
                    self.sessions[key] = ort.InferenceSession(mpath, sess_options=opts)
                    logger.info(f"Loaded ONNX session: {key} from {mpath}")

            self.is_loaded = len(self.sessions) >= 4
        except Exception as e:
            logger.error(f"Failed initializing ONNX sessions: {e}")
            self.is_loaded = False

    def predict_strategy_proba(self, X: np.ndarray) -> np.ndarray:
        """Run ONNX inference for strategy composition probabilities (N, num_classes)."""
        n_samples = X.shape[0] if len(X.shape) > 1 else 1
        n_classes = len(COMPOSITION_CLASSES)
        if not self.is_loaded or "strategy_classifier" not in self.sessions:
            return np.ones((n_samples, n_classes), dtype=np.float32) / n_classes

        sess = self.sessions["strategy_classifier"]
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: X.astype(np.float32)})
        probs = outputs[1] if len(outputs) > 1 else outputs[0]

        if isinstance(probs, list) and len(probs) > 0 and isinstance(probs[0], dict):
            arr = np.zeros((len(probs), n_classes), dtype=np.float32)
            for row_i, row_dict in enumerate(probs):
                for k, v in row_dict.items():
                    if int(k) < n_classes:
                        arr[row_i, int(k)] = v
            return arr

        probs_arr = np.array(probs, dtype=np.float32)
        if probs_arr.ndim == 2 and probs_arr.shape[1] == n_classes:
            return probs_arr
        elif probs_arr.ndim == 2:
            full = np.zeros((n_samples, n_classes), dtype=np.float32)
            full[:, :min(n_classes, probs_arr.shape[1])] = probs_arr[:, :min(n_classes, probs_arr.shape[1])]
            return full
        return probs_arr

    def predict_win_probability(self, X: np.ndarray) -> np.ndarray:
        """Run ONNX inference for match win probability (N,)."""
        if not self.is_loaded or "win_estimator" not in self.sessions:
            n_samples = X.shape[0] if len(X.shape) > 1 else 1
            return np.full((n_samples,), 0.50, dtype=np.float32)

        sess = self.sessions["win_estimator"]
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: X.astype(np.float32)})
        probs = outputs[1] if len(outputs) > 1 else outputs[0]
        if isinstance(probs, list) and len(probs) > 0 and isinstance(probs[0], dict):
            return np.array([row.get(1, 0.5) for row in probs], dtype=np.float32)

        probs_arr = np.array(probs, dtype=np.float32)
        if probs_arr.ndim == 2 and probs_arr.shape[1] == 2:
            return probs_arr[:, 1]
        elif probs_arr.ndim == 2:
            return probs_arr[:, 0]
        return probs_arr

    def predict_economic_ratios(self, X: np.ndarray) -> np.ndarray:
        """Run ONNX inference for gatherer ratio distribution (N, 4)."""
        if not self.is_loaded or "economic_rebalancer" not in self.sessions:
            n_samples = X.shape[0] if len(X.shape) > 1 else 1
            default_r = np.array([0.42, 0.35, 0.20, 0.03], dtype=np.float32)
            return np.tile(default_r, (n_samples, 1))

        sess = self.sessions["economic_rebalancer"]
        input_name = sess.get_inputs()[0].name
        preds = sess.run(None, {input_name: X.astype(np.float32)})[0]
        preds = np.clip(preds, 0.0, 1.0)
        sums = preds.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1.0
        return preds / sums

    def predict_stance_proba(self, X: np.ndarray) -> np.ndarray:
        """Run ONNX inference for tactical stance probabilities (N, num_stances)."""
        n_samples = X.shape[0] if len(X.shape) > 1 else 1
        n_classes = len(STANCE_CLASSES)
        if not self.is_loaded or "stance_predictor" not in self.sessions:
            return np.ones((n_samples, n_classes), dtype=np.float32) / n_classes

        sess = self.sessions["stance_predictor"]
        input_name = sess.get_inputs()[0].name
        outputs = sess.run(None, {input_name: X.astype(np.float32)})
        probs = outputs[1] if len(outputs) > 1 else outputs[0]

        if isinstance(probs, list) and len(probs) > 0 and isinstance(probs[0], dict):
            arr = np.zeros((len(probs), n_classes), dtype=np.float32)
            for row_i, row_dict in enumerate(probs):
                for k, v in row_dict.items():
                    if int(k) < n_classes:
                        arr[row_i, int(k)] = v
            return arr

        probs_arr = np.array(probs, dtype=np.float32)
        if probs_arr.ndim == 2 and probs_arr.shape[1] == n_classes:
            return probs_arr
        elif probs_arr.ndim == 2:
            full = np.zeros((n_samples, n_classes), dtype=np.float32)
            full[:, :min(n_classes, probs_arr.shape[1])] = probs_arr[:, :min(n_classes, probs_arr.shape[1])]
            return full
        return probs_arr
