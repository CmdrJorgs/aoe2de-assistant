"""
AoE2 Economic Rebalancer ML Model:
Predicts high-ELO gatherer distributions (Food, Wood, Gold, Stone)
and generates actionable macro rebalancing instructions.
"""

import os
import joblib
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pydantic import BaseModel, Field
from sklearn.ensemble import RandomForestRegressor
from sklearn.multioutput import MultiOutputRegressor

from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.schemas.match import VillagerAllocation, ResourceStockpile
from aoe2_coach.rules.economy_solver import EconomySolver


class MacroRebalancePlan(BaseModel):
    current_allocation: VillagerAllocation
    target_allocation: VillagerAllocation
    villager_shifts: Dict[str, int] = Field(default_factory=dict)
    shift_instructions: List[str] = Field(default_factory=list)
    floating_stockpile_warnings: List[str] = Field(default_factory=list)
    farm_reseeding_wood_tax_per_sec: float = 0.0
    macro_health_grade: str = "B"
    summary: str = ""


# Standard High-ELO Gatherer Ratio Profiles by Composition Archetype
HIGH_ELO_RATIOS = {
    "knight_line": {"food": 0.45, "wood": 0.25, "gold": 0.28, "stone": 0.02},
    "crossbow_line": {"food": 0.30, "wood": 0.42, "gold": 0.26, "stone": 0.02},
    "pike_line": {"food": 0.42, "wood": 0.48, "gold": 0.08, "stone": 0.02},
    "skirm_line": {"food": 0.38, "wood": 0.52, "gold": 0.08, "stone": 0.02},
    "camel_line": {"food": 0.42, "wood": 0.28, "gold": 0.28, "stone": 0.02},
    "siege_line": {"food": 0.30, "wood": 0.45, "gold": 0.22, "stone": 0.03},
    "monk_line": {"food": 0.32, "wood": 0.28, "gold": 0.38, "stone": 0.02},
    "unique_unit_line": {"food": 0.38, "wood": 0.32, "gold": 0.22, "stone": 0.08},
    "champion_line": {"food": 0.50, "wood": 0.32, "gold": 0.16, "stone": 0.02},
    "scout_line": {"food": 0.55, "wood": 0.38, "gold": 0.05, "stone": 0.02},
}


class EconomicRebalancer:
    """
    Machine Learning Economic Rebalancer:
    Predicts optimal gatherer distribution targets trained against high-ELO macro distributions.
    """

    def __init__(self):
        self.encoder = FeatureEncoder()
        self.solver = EconomySolver()
        self.model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            min_samples_split=4,
            random_state=42,
            n_jobs=-1,
        )
        self.is_trained = False

    def fit(self, X: np.ndarray, Y_ratios: np.ndarray) -> "EconomicRebalancer":
        """
        Fit model on feature matrix X and target villager ratios (N, 4): [pct_f, pct_w, pct_g, pct_s].
        """
        self.model.fit(X, Y_ratios)
        self.is_trained = True
        return self

    def predict_ratios(self, X: np.ndarray) -> np.ndarray:
        """Predict normalized villager proportions (N, 4) summing to 1.0."""
        if not self.is_trained:
            # Default balanced macro distribution
            n_samples = X.shape[0] if len(X.shape) > 1 else 1
            default_r = np.array([0.42, 0.35, 0.20, 0.03], dtype=np.float32)
            return np.tile(default_r, (n_samples, 1))

        raw_preds = self.model.predict(X)
        # Ensure non-negative and normalize each row to sum to 1.0
        preds = np.clip(raw_preds, 0.0, 1.0)
        sums = preds.sum(axis=1, keepdims=True)
        sums[sums == 0] = 1.0
        return preds / sums

    def recommend_rebalance(
        self,
        state_or_vector: Union[Dict[str, Any], np.ndarray],
        current_vills: Optional[VillagerAllocation] = None,
        current_stockpile: Optional[ResourceStockpile] = None,
        strategy_comp: str = "knight_line",
        custom_ratios: Optional[np.ndarray] = None,
    ) -> MacroRebalancePlan:
        """
        Generate actionable macro rebalancing steps and gatherer shifts.
        """
        if isinstance(state_or_vector, dict):
            X = self.encoder.encode_dict(state_or_vector).reshape(1, -1)
            raw = state_or_vector
            tot_vills = int(raw.get("vills_total", raw.get("player_vills_total", 35)))
            if current_vills is None:
                current_vills = VillagerAllocation(
                    total=tot_vills,
                    food=int(raw.get("vills_food", raw.get("player_vills_food", 14))),
                    wood=int(raw.get("vills_wood", raw.get("player_vills_wood", 14))),
                    gold=int(raw.get("vills_gold", raw.get("player_vills_gold", 7))),
                    stone=int(raw.get("vills_stone", raw.get("player_vills_stone", 0))),
                )
            if current_stockpile is None:
                current_stockpile = ResourceStockpile(
                    food=int(raw.get("food", raw.get("player_food", 200))),
                    wood=int(raw.get("wood", raw.get("player_wood", 200))),
                    gold=int(raw.get("gold", raw.get("player_gold", 100))),
                    stone=int(raw.get("stone", raw.get("player_stone", 0))),
                )
        elif isinstance(state_or_vector, np.ndarray):
            X = state_or_vector.reshape(1, -1) if state_or_vector.ndim == 1 else state_or_vector
            tot_vills = current_vills.total if current_vills else 35
            if current_vills is None:
                current_vills = VillagerAllocation(total=tot_vills, food=14, wood=14, gold=7, stone=0)
            if current_stockpile is None:
                current_stockpile = ResourceStockpile(food=200, wood=200, gold=100, stone=0)
        else:
            raise TypeError(f"Unsupported input type: {type(state_or_vector)}")

        # 1. Predict ML gatherer ratios
        if custom_ratios is not None:
            ratios = custom_ratios
        else:
            ratios = self.predict_ratios(X)[0]
        # Blend with domain archetype prior if specified
        if strategy_comp in HIGH_ELO_RATIOS:
            prior = HIGH_ELO_RATIOS[strategy_comp]
            r_food = (ratios[0] * 0.6) + (prior["food"] * 0.4)
            r_wood = (ratios[1] * 0.6) + (prior["wood"] * 0.4)
            r_gold = (ratios[2] * 0.6) + (prior["gold"] * 0.4)
            r_stone = (ratios[3] * 0.6) + (prior["stone"] * 0.4)
        else:
            r_food, r_wood, r_gold, r_stone = ratios[0], ratios[1], ratios[2], ratios[3]

        r_sum = r_food + r_wood + r_gold + r_stone
        r_food /= r_sum
        r_wood /= r_sum
        r_gold /= r_sum
        r_stone /= r_sum

        # Calculate integer target villagers
        tgt_food = round(tot_vills * r_food)
        tgt_wood = round(tot_vills * r_wood)
        tgt_gold = round(tot_vills * r_gold)
        tgt_stone = round(tot_vills * r_stone)

        # Fix rounding differences
        diff = tot_vills - (tgt_food + tgt_wood + tgt_gold + tgt_stone)
        tgt_wood += diff

        target_allocation = VillagerAllocation(
            total=tot_vills,
            food=max(0, tgt_food),
            wood=max(0, tgt_wood),
            gold=max(0, tgt_gold),
            stone=max(0, tgt_stone),
            idle_rate=0.0,
        )

        # Compute shifts (Target - Current)
        shifts = {
            "food": target_allocation.food - current_vills.food,
            "wood": target_allocation.wood - current_vills.wood,
            "gold": target_allocation.gold - current_vills.gold,
            "stone": target_allocation.stone - current_vills.stone,
        }

        # Check floating stockpiles & generate instructions
        warnings: List[str] = []
        instructions: List[str] = []

        if current_stockpile.wood >= 600 and current_stockpile.food < 200:
            warnings.append(f"Floating wood ({current_stockpile.wood}) while starving on food ({current_stockpile.food}).")
            if shifts["wood"] < 0 and shifts["food"] > 0:
                instructions.append(f"Move {abs(shifts['wood'])} woodchoppers directly to build and reseed Farms.")
        elif current_stockpile.wood >= 600 and current_stockpile.gold < 100:
            warnings.append(f"Excess wood stockpile ({current_stockpile.wood}) with gold deficit ({current_stockpile.gold}).")
            instructions.append(f"Transfer {abs(shifts['wood'])} woodchoppers to Gold Mining Camps.")

        if shifts["food"] > 2 and not instructions:
            instructions.append(f"Add {shifts['food']} more villagers to Farms/Food.")
        if shifts["gold"] > 2:
            instructions.append(f"Assign {shifts['gold']} more villagers to Gold.")
        if shifts["wood"] > 2:
            instructions.append(f"Send {shifts['wood']} newly spawned villagers to Woodlines.")

        if not instructions:
            instructions.append("Economy is well balanced. Maintain current gatherer distribution.")

        # Evaluate macro health grade
        shift_magnitude = sum(abs(v) for v in shifts.values())
        if shift_magnitude <= 2 and not warnings:
            grade = "A"
        elif shift_magnitude <= 6:
            grade = "B"
        elif shift_magnitude <= 12:
            grade = "C"
        else:
            grade = "D"

        # Farm wood tax estimate
        farm_tax = round(0.35 * target_allocation.food * (60.0 / 250.0), 2)

        summary = (
            f"Macro Target for {strategy_comp.replace('_', ' ').title()}: "
            f"{target_allocation.food} Food | {target_allocation.wood} Wood | {target_allocation.gold} Gold | {target_allocation.stone} Stone."
        )

        return MacroRebalancePlan(
            current_allocation=current_vills,
            target_allocation=target_allocation,
            villager_shifts=shifts,
            shift_instructions=instructions,
            floating_stockpile_warnings=warnings,
            farm_reseeding_wood_tax_per_sec=farm_tax,
            macro_health_grade=grade,
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

    def load(self, filepath: str) -> "EconomicRebalancer":
        """Load persisted model weights."""
        data = joblib.load(filepath)
        self.model = data["model"]
        self.is_trained = data["is_trained"]
        return self
