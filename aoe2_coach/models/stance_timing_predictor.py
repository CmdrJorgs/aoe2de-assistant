"""
AoE2 Stance & Timing Window Predictor:
Classifies strategic posture (Aggressive, Forward Pressure, Defensive, Boom, Relic Control)
and computes power spike attack windows and opponent timing threats.
"""

import os
import joblib
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from aoe2_coach.models.feature_encoder import FeatureEncoder


STANCE_CLASSES = [
    "ALL_IN_AGGRESSION",
    "FORWARD_PRESSURE",
    "DEFENSIVE_TURTLING",
    "FAST_IMPERIAL_BOOM",
    "RELIC_HILL_CONTROL",
]

STANCE_DESCRIPTIONS = {
    "ALL_IN_AGGRESSION": "Maximum forward pressure. Spend all resources on military production and break enemy defenses before they scale.",
    "FORWARD_PRESSURE": "Controlled military raiding. Deny enemy expansions and map resources while sustaining eco behind.",
    "DEFENSIVE_TURTLING": "Absorb enemy push behind fortifications, defensive siege, and walls while massing counter-composition.",
    "FAST_IMPERIAL_BOOM": "Heavy eco investment with multi-TC boom to race toward Imperial Age technology and Trebuchet advantage.",
    "RELIC_HILL_CONTROL": "Secure high-ground positions, neutral gold/stone piles, and Monastery relics for long-term gold advantage.",
}


class StanceTimingResult(BaseModel):
    recommended_stance: str
    stance_confidence: float
    attack_window_sec: int
    urgency: str
    civ_power_spike: str
    threat_spike_alert: str
    summary: str = ""


class StanceTimingPredictor:
    """
    Machine Learning Stance & Timing Window Predictor.
    Evaluates military readiness, timing power spikes, and tactical posture.
    """

    def __init__(self):
        self.encoder = FeatureEncoder()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(STANCE_CLASSES)
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def fit(self, X: np.ndarray, y_stance: List[str]) -> "StanceTimingPredictor":
        """Fit model on state features and tactical stance labels."""
        y_encoded = self.label_encoder.transform(y_stance)
        self.model.fit(X, y_encoded)
        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities (N, num_stances)."""
        n_samples = X.shape[0] if len(X.shape) > 1 else 1
        n_classes = len(STANCE_CLASSES)
        if not self.is_trained:
            return np.ones((n_samples, n_classes), dtype=np.float32) / float(n_classes)

        raw_probs = self.model.predict_proba(X)
        if raw_probs.shape[1] == n_classes:
            return raw_probs.astype(np.float32)

        full_probs = np.zeros((n_samples, n_classes), dtype=np.float32)
        for col_idx, class_idx in enumerate(self.model.classes_):
            full_probs[:, class_idx] = raw_probs[:, col_idx]
        return full_probs

    def evaluate_timing_and_stance(
        self,
        state_or_vector: Union[Dict[str, Any], np.ndarray],
        player_civ: Optional[str] = None,
        opponent_civ: Optional[str] = None,
        player_age: int = 3,
        game_time_sec: float = 1200.0,
    ) -> StanceTimingResult:
        """
        Predict tactical stance and calculate precise timing window and power spike dynamics.
        """
        if isinstance(state_or_vector, dict):
            X = self.encoder.encode_dict(state_or_vector).reshape(1, -1)
            raw = state_or_vector
            player_civ = str(raw.get("player_civ", raw.get("player_civ_name", player_civ or "Franks"))).lower()
            opponent_civ = str(raw.get("opponent_civ", raw.get("opponent_civ_name", opponent_civ or "Vikings"))).lower()
            player_age = int(raw.get("player_age", player_age))
            game_time_sec = float(raw.get("timestamp_sec", game_time_sec))
        elif isinstance(state_or_vector, np.ndarray):
            X = state_or_vector.reshape(1, -1) if state_or_vector.ndim == 1 else state_or_vector
            player_civ = (player_civ or "Franks").lower()
            opponent_civ = (opponent_civ or "Vikings").lower()
        else:
            raise TypeError(f"Unsupported input type: {type(state_or_vector)}")

        probs = self.predict_proba(X)[0]
        top_idx = int(np.argmax(probs))
        top_stance = self.label_encoder.classes_[top_idx]
        confidence = float(probs[top_idx])

        # Evaluate power spikes & timing window based on match dynamics
        civ_power_spike = ""
        threat_alert = ""
        attack_window_sec = 240
        urgency = "medium"

        # Civ specific power spike knowledge
        if player_civ == "franks" and player_age == 3:
            civ_power_spike = "Castle Age Knight HP Power Spike (+20% HP). Strike before enemy accumulates massed halberdiers or camels."
            attack_window_sec = 180
            urgency = "immediate"
        elif player_civ == "britons" and player_age in (2, 3):
            civ_power_spike = "Archery Range (+1/+2) Range Advantage. Establish hill control and kite enemy infantry."
            attack_window_sec = 240
        elif player_civ == "goths" and player_age == 4:
            civ_power_spike = "Imperial Age Anarchy + Perfusion flood. Overwhelm enemy defenses with endless cheap infantry."
            attack_window_sec = 300
            urgency = "immediate"
        else:
            civ_power_spike = f"{player_civ.title()} Age {player_age} strategic window."

        # Opponent threat spike warnings
        if opponent_civ == "vikings" and player_age == 3:
            threat_alert = "Warning: Do not allow Vikings to mass Elite Berserkers with Berserkergang in Imperial Age. Strike now!"
        elif opponent_civ == "turks" and player_age == 3:
            threat_alert = "Warning: Fast Imperial Gunpowder / Bombard Cannon timing danger from Turks."
        elif opponent_civ == "mongols" and player_age in (3, 4):
            threat_alert = "Warning: Mongol Drill Mangudai and Siege Onager deathball in late Imperial. End match early."

        if top_stance == "ALL_IN_AGGRESSION":
            urgency = "immediate"
            attack_window_sec = min(180, attack_window_sec)
        elif top_stance == "DEFENSIVE_TURTLING":
            urgency = "defend_now"

        summary = (
            f"Tactical Stance: {top_stance.replace('_', ' ').title()} ({round(confidence * 100)}% conf). "
            f"{STANCE_DESCRIPTIONS.get(top_stance, '')}"
        )

        return StanceTimingResult(
            recommended_stance=top_stance,
            stance_confidence=round(confidence, 4),
            attack_window_sec=attack_window_sec,
            urgency=urgency,
            civ_power_spike=civ_power_spike,
            threat_spike_alert=threat_alert,
            summary=summary,
        )

    def save(self, filepath: str) -> None:
        """Persist trained model weights."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(
            {
                "model": self.model,
                "label_encoder": self.label_encoder,
                "is_trained": self.is_trained,
            },
            filepath,
        )

    def load(self, filepath: str) -> "StanceTimingPredictor":
        """Load persisted model weights."""
        data = joblib.load(filepath)
        self.model = data["model"]
        self.label_encoder = data["label_encoder"]
        self.is_trained = data["is_trained"]
        return self
