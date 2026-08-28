"""
AoE2 Strategy Classifier Model: Predicts optimal military compositions,
production building deployments, and technology priorities from game states.
"""

import os
import joblib
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

from aoe2_coach.models.feature_encoder import FeatureEncoder


# Standard Canonical Composition Targets
COMPOSITION_CLASSES = [
    "knight_line",
    "crossbow_line",
    "pike_line",
    "skirm_line",
    "camel_line",
    "siege_line",
    "monk_line",
    "unique_unit_line",
    "champion_line",
    "scout_line",
]

BUILDING_CLASSES = [
    "stable",
    "archery_range",
    "barracks",
    "siege_workshop",
    "monastery",
    "castle",
    "town_center",
]

TECH_CLASSES = [
    "cavalry_upgrades",
    "archer_upgrades",
    "infantry_upgrades",
    "siege_upgrades",
    "eco_upgrades",
    "age_up",
]


class CompositionRanking(BaseModel):
    composition: str
    confidence: float
    recommended_building: str
    key_technologies: List[str]
    strategic_rationale: str


class StrategyPrediction(BaseModel):
    primary_composition: str
    confidence: float
    secondary_composition: Optional[str] = None
    recommended_building: str
    recommended_tech_focus: str
    rankings: List[CompositionRanking] = Field(default_factory=list)
    strategic_summary: str = ""


# Strategy Rationale and Details Mapping
STRATEGY_DETAILS = {
    "knight_line": {
        "building": "stable",
        "techs": ["scale_barding_armor", "bloodlines", "husbandry"],
        "rationale": "Heavy cavalry mobility and shock DPS. Overwhelms archers and unfortified positions.",
    },
    "crossbow_line": {
        "building": "archery_range",
        "techs": ["bodkin_arrow", "padded_archer_armor", "ballistics"],
        "rationale": "Massed ranged firepower and choke point control. Out-ranges infantry and soft targets.",
    },
    "pike_line": {
        "building": "barracks",
        "techs": ["scale_mail_armor", "iron_casting", "squires"],
        "rationale": "Cost-efficient anti-cavalry defense. Hard counters heavy cavalry and raiding.",
    },
    "skirm_line": {
        "building": "archery_range",
        "techs": ["bodkin_arrow", "leather_archer_armor", "ballistics"],
        "rationale": "High pierce armor trash counter against massed archers and crossbows.",
    },
    "camel_line": {
        "building": "stable",
        "techs": ["scale_barding_armor", "bloodlines", "husbandry"],
        "rationale": "Fast anti-cavalry cavalry with bonus damage against Knights and cavalry archers.",
    },
    "siege_line": {
        "building": "siege_workshop",
        "techs": ["siege_engineers", "chemistry"],
        "rationale": "Heavy area-of-effect damage against clumped archers and rapid building demolition.",
    },
    "monk_line": {
        "building": "monastery",
        "techs": ["sanctity", "redemption", "fervor", "atonement"],
        "rationale": "High-value conversion support against expensive cavalry, knights, and siege.",
    },
    "unique_unit_line": {
        "building": "castle",
        "techs": ["conscription"],
        "rationale": "Leverage civilization unique unit power spike and civilization-defining bonuses.",
    },
    "champion_line": {
        "building": "barracks",
        "techs": ["supplies", "gambesons", "iron_casting", "squires"],
        "rationale": "High melee damage swarm to shred trash units, skirmishers, eagles, and buildings.",
    },
    "scout_line": {
        "building": "stable",
        "techs": ["bloodlines", "husbandry", "forging"],
        "rationale": "Food-only trash raiding force with conversion resistance against monks and backline eco.",
    },
}


def map_label_to_canonical_comp(label: str) -> str:
    """Normalize arbitrary raw replay labels to one of the canonical 10 compositions."""
    lbl = str(label).lower().replace(" ", "_")
    if any(k in lbl for k in ["knight", "cavalier", "paladin", "heavy_cav", "monaspa", "boyar", "coustillier"]):
        return "knight_line"
    elif any(k in lbl for k in ["crossbow", "archer", "arbalester", "plumed", "longbow", "chu_ko_nu", "rattan", "composite_bowman"]):
        return "crossbow_line"
    elif any(k in lbl for k in ["spear", "pike", "halberdier"]):
        return "pike_line"
    elif any(k in lbl for k in ["skirm", "genitour"]):
        return "skirm_line"
    elif any(k in lbl for k in ["camel", "mameluke", "shrivamsha"]):
        return "camel_line"
    elif any(k in lbl for k in ["mangonel", "onager", "scorpion", "ram", "bombard", "siege", "organ_gun"]):
        return "siege_line"
    elif any(k in lbl for k in ["monk", "missionary"]):
        return "monk_line"
    elif any(k in lbl for k in ["unique", "castle_unit", "berserk", "huskarl", "samurai", "jaguar", "woad", "conquistador", "leitis", "obuch", "urumi"]):
        return "unique_unit_line"
    elif any(k in lbl for k in ["militia", "man_at_arms", "long_swordsman", "swordsman", "two_handed", "champion", "infantry"]):
        return "champion_line"
    elif any(k in lbl for k in ["scout", "light_cav", "hussar", "steppe_lancer"]):
        return "scout_line"
    return "knight_line"


class StrategyClassifier:
    """
    Machine Learning Strategy Classifier.
    Predicts optimal military compositions, supporting units, and tech priorities.
    """

    def __init__(self):
        self.encoder = FeatureEncoder()
        self.label_encoder = LabelEncoder()
        self.label_encoder.fit(COMPOSITION_CLASSES)
        
        # Primary composition classifier (HistGradientBoosting / RandomForest)
        self.comp_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=12,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def fit(
        self,
        X: np.ndarray,
        y_comp: List[str],
    ) -> "StrategyClassifier":
        """Fit model on encoded feature matrix X and target composition labels."""
        y_mapped = [map_label_to_canonical_comp(lbl) for lbl in y_comp]
        y_encoded = self.label_encoder.transform(y_mapped)

        self.comp_model.fit(X, y_encoded)
        self.is_trained = True
        return self

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Predict class probabilities (N, num_classes)."""
        n_samples = X.shape[0] if len(X.shape) > 1 else 1
        n_classes = len(COMPOSITION_CLASSES)
        if not self.is_trained:
            # Return uniform prior / heuristic probabilities
            return np.ones((n_samples, n_classes), dtype=np.float32) / float(n_classes)
        
        raw_probs = self.comp_model.predict_proba(X)
        if raw_probs.shape[1] == n_classes:
            return raw_probs.astype(np.float32)

        # Map observed model classes to full classes
        full_probs = np.zeros((n_samples, n_classes), dtype=np.float32)
        for col_idx, class_idx in enumerate(self.comp_model.classes_):
            full_probs[:, class_idx] = raw_probs[:, col_idx]
        return full_probs

    def predict_single(
        self,
        state_or_vector: Union[Dict[str, Any], np.ndarray],
    ) -> StrategyPrediction:
        """Predict full strategy recommendation for a single game state."""
        if isinstance(state_or_vector, dict):
            X = self.encoder.encode_dict(state_or_vector).reshape(1, -1)
        elif isinstance(state_or_vector, np.ndarray):
            X = state_or_vector.reshape(1, -1) if state_or_vector.ndim == 1 else state_or_vector
        else:
            raise TypeError(f"Unsupported input type: {type(state_or_vector)}")

        probs = self.predict_proba(X)[0]
        sorted_indices = np.argsort(probs)[::-1]

        rankings: List[CompositionRanking] = []
        for idx in sorted_indices:
            comp_name = self.label_encoder.classes_[idx]
            conf = float(probs[idx])
            details = STRATEGY_DETAILS.get(comp_name, {
                "building": "archery_range",
                "techs": [],
                "rationale": f"Produce {comp_name.replace('_', ' ').title()}",
            })
            rankings.append(
                CompositionRanking(
                    composition=comp_name,
                    confidence=round(conf, 4),
                    recommended_building=details["building"],
                    key_technologies=details["techs"],
                    strategic_rationale=details["rationale"],
                )
            )

        top = rankings[0]
        second = rankings[1] if len(rankings) > 1 else None

        # Build human-readable summary
        summary = (
            f"Recommended Primary Composition: {top.composition.replace('_', ' ').title()} "
            f"({round(top.confidence * 100, 1)}% confidence) produced from {top.recommended_building.replace('_', ' ').title()}. "
            f"{top.strategic_rationale}"
        )

        return StrategyPrediction(
            primary_composition=top.composition,
            confidence=top.confidence,
            secondary_composition=second.composition if second and second.confidence > 0.15 else None,
            recommended_building=top.recommended_building,
            recommended_tech_focus=top.key_technologies[0] if top.key_technologies else "none",
            rankings=rankings,
            strategic_summary=summary,
        )

    def save(self, filepath: str) -> None:
        """Persist trained model weights and label encoders."""
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        joblib.dump(
            {
                "comp_model": self.comp_model,
                "label_encoder": self.label_encoder,
                "is_trained": self.is_trained,
            },
            filepath,
        )

    def load(self, filepath: str) -> "StrategyClassifier":
        """Load persisted model weights and label encoders."""
        data = joblib.load(filepath)
        self.comp_model = data["comp_model"]
        self.label_encoder = data["label_encoder"]
        self.is_trained = data["is_trained"]
        return self
