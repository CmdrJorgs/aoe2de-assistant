"""
AoE2 Win Probability Estimator (Value Model):
Estimates real-time match win probability P(Win | State) and evaluates strategic advantages.
"""

import os
import joblib
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.calibration import CalibratedClassifierCV

from aoe2_coach.models.feature_encoder import FeatureEncoder


class WinProbabilityResult(BaseModel):
    win_probability: float
    advantage_level: str
    eco_advantage_score: float
    military_advantage_score: float
    civ_matchup_score: float
    key_win_factors: List[str] = Field(default_factory=list)
    summary: str = ""


def classify_advantage_level(prob: float) -> str:
    """Convert numeric win probability to human-readable advantage tier."""
    if prob >= 0.85:
        return "dominant_lead"
    elif prob >= 0.70:
        return "moderate_lead"
    elif prob >= 0.55:
        return "slight_advantage"
    elif prob >= 0.45:
        return "even_match"
    elif prob >= 0.30:
        return "slight_disadvantage"
    elif prob >= 0.15:
        return "moderate_deficit"
    else:
        return "critical_deficit"


class WinProbabilityEstimator:
    """
    Machine Learning Value Model: Estimates P(Win | State).
    Evaluates military superiority, eco health, and civ matchup dynamics.
    """

    def __init__(self):
        self.encoder = FeatureEncoder()
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def fit(self, X: np.ndarray, y_winner: Union[List[bool], np.ndarray]) -> "WinProbabilityEstimator":
        """Fit model on state features and binary win/loss targets."""
        y_arr = np.array(y_winner, dtype=np.int32)
        self.model.fit(X, y_arr)
        self.is_trained = True
        return self

    def predict_win_probability(self, X: np.ndarray) -> np.ndarray:
        """Predict win probability P(Win=1) for batch of feature vectors (N,)."""
        if not self.is_trained:
            # Untrained baseline heuristic
            n_samples = X.shape[0] if len(X.shape) > 1 else 1
            return np.full((n_samples,), 0.50, dtype=np.float32)
        probs = self.model.predict_proba(X)
        if probs.shape[1] == 2:
            return probs[:, 1]
        return probs[:, 0]

    def evaluate(
        self,
        state_or_vector: Union[Dict[str, Any], np.ndarray],
    ) -> WinProbabilityResult:
        """Evaluate win probability and provide explainable factor analysis."""
        if isinstance(state_or_vector, dict):
            X = self.encoder.encode_dict(state_or_vector).reshape(1, -1)
            raw_dict = state_or_vector
        elif isinstance(state_or_vector, np.ndarray):
            X = state_or_vector.reshape(1, -1) if state_or_vector.ndim == 1 else state_or_vector
            raw_dict = {}
        else:
            raise TypeError(f"Unsupported input type: {type(state_or_vector)}")

        prob = float(self.predict_win_probability(X)[0])
        prob = max(0.01, min(0.99, prob))
        adv_level = classify_advantage_level(prob)

        # Compute factor score breakdowns from state vector
        vec = X[0]
        # vec indices based on FeatureEncoder:
        # 17: vills_total, 26: military_total, 34: opp_mil_tot, 60: rel_mil_adv, 61: rel_vill_adv
        mil_adv = float(vec[60]) if len(vec) > 60 else 0.0
        vill_adv = float(vec[61]) if len(vec) > 61 else 0.0
        p_cav_aff = float(vec[50]) if len(vec) > 50 else 0.5
        opp_cav_aff = float(vec[55]) if len(vec) > 55 else 0.5
        civ_score = (p_cav_aff - opp_cav_aff) * 0.2

        factors: List[str] = []
        if vill_adv > 0.15:
            factors.append(f"Strong economy & villager production momentum (+{round(vill_adv * 100)}% ahead)")
        elif vill_adv < -0.15:
            factors.append(f"Economy lagging behind standard benchmarks ({round(vill_adv * 100)}% deficit)")

        if mil_adv > 0.20:
            factors.append(f"Military superiority and map control presence (+{round(mil_adv * 100)}% army power)")
        elif mil_adv < -0.20:
            factors.append(f"Vulnerable to enemy military push ({round(abs(mil_adv) * 100)}% army deficit)")

        is_floating_w = float(vec[14]) if len(vec) > 14 else 0.0
        if is_floating_w > 0.5:
            factors.append("Unspent stockpile floating: Excess wood delaying farm & military output")

        if not factors:
            factors.append("Match is in a closely contested balanced state")

        summary = f"Estimated Win Probability: {round(prob * 100, 1)}% ({adv_level.replace('_', ' ').title()})."

        return WinProbabilityResult(
            win_probability=round(prob, 4),
            advantage_level=adv_level,
            eco_advantage_score=round(vill_adv, 3),
            military_advantage_score=round(mil_adv, 3),
            civ_matchup_score=round(civ_score, 3),
            key_win_factors=factors,
            summary=summary,
        )

    def save(self, filepath: str) -> None:
        """Persist trained model weights."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "is_trained": self.is_trained,
            },
            filepath,
        )

    def load(self, filepath: str) -> "WinProbabilityEstimator":
        """Load persisted model weights."""
        data = joblib.load(filepath)
        self.model = data["model"]
        self.is_trained = data["is_trained"]
        return self
