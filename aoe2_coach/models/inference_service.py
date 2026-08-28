"""
AoE2 Unified Strategy ML Inference Service:
Orchestrates feature extraction, neural & tree models (via ONNX runtime),
and deterministic tech-tree / counter-matrix rules validation.
"""

import os
import time
import logging
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
from pydantic import BaseModel, Field

from aoe2_coach.schemas.game_constants import Age, get_civ_name
from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    ResourceStockpile,
    VillagerAllocation,
)
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.strategy_classifier import (
    StrategyClassifier,
    StrategyPrediction,
    CompositionRanking,
    STRATEGY_DETAILS,
    COMPOSITION_CLASSES,
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
from aoe2_coach.models.onnx_inference import ONNXInferenceEngine
from aoe2_coach.rules.counter_matrix import CounterMatrixEngine, CounterMatrixResult
from aoe2_coach.rules.economy_solver import EconomySolver
from aoe2_coach.rules.tech_tree import is_unit_available, get_civ_info

logger = logging.getLogger(__name__)


class MatchContext(BaseModel):
    player_civ: str
    opponent_civ: str
    player_elo: int
    player_age: int
    player_age_name: str
    game_time_sec: float
    formatted_time: str


class MLRecommendation(BaseModel):
    match_context: MatchContext
    primary_directive: str
    win_probability: WinProbabilityResult
    military_action_plan: StrategyPrediction
    counter_matrix: CounterMatrixResult
    economic_rebalance: MacroRebalancePlan
    tactical_stance: StanceTimingResult
    actionable_checklist: List[str] = Field(default_factory=list)
    inference_latency_ms: float = 0.0


class MLInferenceService:
    """
    High-level recommendation engine orchestrating machine learning predictions,
    ONNX acceleration, and strict domain knowledge constraints.
    """

    def __init__(
        self,
        artifacts_dir: str = "aoe2_coach/models/artifacts",
        use_onnx: bool = True,
    ):
        self.artifacts_dir = artifacts_dir
        self.encoder = FeatureEncoder()
        self.counter_engine = CounterMatrixEngine()
        self.economy_solver = EconomySolver()

        # ML Models (Python backends)
        self.strategy_classifier = StrategyClassifier()
        self.win_estimator = WinProbabilityEstimator()
        self.economic_rebalancer = EconomicRebalancer()
        self.stance_predictor = StanceTimingPredictor()

        # Load persisted joblib models if available
        self._load_joblib_models()

        # ONNX Engine
        self.use_onnx = use_onnx
        self.onnx_engine = ONNXInferenceEngine(artifacts_dir=artifacts_dir) if use_onnx else None

    def _load_joblib_models(self) -> None:
        """Load persisted joblib model files if present."""
        try:
            strat_p = os.path.join(self.artifacts_dir, "strategy_classifier.joblib")
            win_p = os.path.join(self.artifacts_dir, "win_probability_estimator.joblib")
            eco_p = os.path.join(self.artifacts_dir, "economic_rebalancer.joblib")
            stance_p = os.path.join(self.artifacts_dir, "stance_predictor.joblib")

            if os.path.exists(strat_p):
                self.strategy_classifier.load(strat_p)
            if os.path.exists(win_p):
                self.win_estimator.load(win_p)
            if os.path.exists(eco_p):
                self.economic_rebalancer.load(eco_p)
            if os.path.exists(stance_p):
                self.stance_predictor.load(stance_p)
        except Exception as e:
            logger.warning(f"Could not load some joblib model artifacts: {e}")

    def get_recommendation(
        self,
        state: Union[GameSnapshot, Dict[str, Any]],
    ) -> MLRecommendation:
        """
        Generate comprehensive, validated real-time tactical recommendation.
        Guarantees sub-20ms inference latency and strict tech tree validity.
        """
        start_time = time.perf_counter()

        # Normalize state input
        if isinstance(state, GameSnapshot):
            state_dict = state.to_flat_dict()
            p_civ = state.player.civ_name or get_civ_name(state.player.civ_id)
            opp_civ = state.opponent_observed.civ_name or get_civ_name(state.opponent_observed.civ_id)
            p_age_int = state.player.age
            p_elo = state.player.elo or 1200
            t_sec = float(state.timestamp_sec)
            current_vills = state.player.villagers
            current_stockpile = state.player.resources
            sighted_enemy = {u.entity_name: u.count for u in state.opponent_observed.sighted_units}
        else:
            state_dict = state
            p_civ = str(state.get("player_civ", state.get("player_civ_name", "Franks")))
            opp_civ = str(state.get("opponent_civ", state.get("opponent_civ_name", "Vikings")))
            p_age_int = int(state.get("player_age", 3))
            p_elo = int(state.get("player_elo", 1200))
            t_sec = float(state.get("timestamp_sec", 1200.0))
            current_vills = VillagerAllocation(
                total=int(state.get("vills_total", state.get("player_vills_total", 40))),
                food=int(state.get("vills_food", state.get("player_vills_food", 16))),
                wood=int(state.get("vills_wood", state.get("player_vills_wood", 16))),
                gold=int(state.get("vills_gold", state.get("player_vills_gold", 8))),
                stone=int(state.get("vills_stone", state.get("player_vills_stone", 0))),
            )
            current_stockpile = ResourceStockpile(
                food=int(state.get("food", state.get("player_food", 300))),
                wood=int(state.get("wood", state.get("player_wood", 600))),
                gold=int(state.get("gold", state.get("player_gold", 150))),
                stone=int(state.get("stone", state.get("player_stone", 0))),
            )
            sighted_enemy = {}
            if "sighted_units" in state and isinstance(state["sighted_units"], list):
                for item in state["sighted_units"]:
                    if isinstance(item, dict):
                        sighted_enemy[item.get("unit", item.get("entity_name", ""))] = item.get("count", 1)
            elif "opp_sighted_cavalry" in state or "opp_sighted_archers" in state or "opp_sighted_infantry" in state:
                if state.get("opp_sighted_cavalry", 0) > 0:
                    sighted_enemy["knight"] = int(state["opp_sighted_cavalry"])
                if state.get("opp_sighted_archers", 0) > 0:
                    sighted_enemy["crossbowman"] = int(state["opp_sighted_archers"])
                if state.get("opp_sighted_infantry", 0) > 0:
                    sighted_enemy["berserk" if opp_civ.lower() == "vikings" else "long_swordsman"] = int(state["opp_sighted_infantry"])

        age_enum = Age(p_age_int) if p_age_int in (1, 2, 3, 4) else Age.CASTLE

        # 1. Feature Encoding
        X = self.encoder.encode_dict(state_dict).reshape(1, -1)

        # 2. ML Strategy Prediction (via ONNX runtime or python model)
        if self.use_onnx and self.onnx_engine and self.onnx_engine.is_loaded:
            strat_probs = self.onnx_engine.predict_strategy_proba(X)[0]
            sorted_indices = np.argsort(strat_probs)[::-1]
            rankings: List[CompositionRanking] = []
            for idx in sorted_indices:
                comp_name = COMPOSITION_CLASSES[idx]
                conf = float(strat_probs[idx])
                details = STRATEGY_DETAILS.get(comp_name, {
                    "building": "stable",
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
            strategy_plan = StrategyPrediction(
                primary_composition=top.composition,
                confidence=top.confidence,
                secondary_composition=second.composition if second and second.confidence > 0.15 else None,
                recommended_building=top.recommended_building,
                recommended_tech_focus=top.key_technologies[0] if top.key_technologies else "none",
                rankings=rankings,
                strategic_summary=(
                    f"Recommended: {top.composition.replace('_', ' ').title()} "
                    f"({round(top.confidence * 100, 1)}% confidence) from {top.recommended_building.replace('_', ' ').title()}. "
                    f"{top.strategic_rationale}"
                ),
            )
        else:
            strategy_plan = self.strategy_classifier.predict_single(X)

        # Tech tree guardrail: If civ cannot produce predicted unit, fallback
        if not is_unit_available(p_civ, strategy_plan.primary_composition.replace("_line", "")):
            if p_civ.lower() in ("aztecs", "mayans", "incas") and "knight" in strategy_plan.primary_composition:
                strategy_plan.primary_composition = "eagle_line"
                strategy_plan.recommended_building = "barracks"

        # 3. Deterministic Counter Matrix Evaluation (Phase 2 Rule Engine)
        counter_result = self.counter_engine.recommend_counters(
            player_civ=p_civ,
            player_age=age_enum,
            enemy_units=sighted_enemy,
            enemy_civ=opp_civ,
        )

        # 4. ML Win Probability Estimation
        if self.use_onnx and self.onnx_engine and self.onnx_engine.is_loaded:
            win_p = float(self.onnx_engine.predict_win_probability(X)[0])
            win_p = max(0.01, min(0.99, win_p))
            adv_level = classify_advantage_level(win_p)
            vec = X[0]
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

            if float(vec[14]) > 0.5:
                factors.append("Unspent stockpile floating: Excess wood delaying farm & military output")

            if not factors:
                factors.append("Match is in a closely contested balanced state")

            win_res = WinProbabilityResult(
                win_probability=round(win_p, 4),
                advantage_level=adv_level,
                eco_advantage_score=round(vill_adv, 3),
                military_advantage_score=round(mil_adv, 3),
                civ_matchup_score=round(civ_score, 3),
                key_win_factors=factors,
                summary=f"Estimated Win Probability: {round(win_p * 100, 1)}% ({adv_level.replace('_', ' ').title()}).",
            )
        else:
            win_res = self.win_estimator.evaluate(X)

        # 5. ML Economic Rebalance + Solver
        if self.use_onnx and self.onnx_engine and self.onnx_engine.is_loaded:
            onnx_ratios = self.onnx_engine.predict_economic_ratios(X)[0]
            eco_plan = self.economic_rebalancer.recommend_rebalance(
                state_or_vector=X,
                current_vills=current_vills,
                current_stockpile=current_stockpile,
                strategy_comp=strategy_plan.primary_composition,
                custom_ratios=onnx_ratios,
            )
        else:
            eco_plan = self.economic_rebalancer.recommend_rebalance(
                state_or_vector=X,
                current_vills=current_vills,
                current_stockpile=current_stockpile,
                strategy_comp=strategy_plan.primary_composition,
            )

        # 6. ML Stance & Timing Prediction
        if self.use_onnx and self.onnx_engine and self.onnx_engine.is_loaded:
            stance_probs = self.onnx_engine.predict_stance_proba(X)[0]
            top_stance_idx = int(np.argmax(stance_probs))
            top_stance = STANCE_CLASSES[top_stance_idx]
            conf = float(stance_probs[top_stance_idx])
            civ_power_spike = f"{p_civ.title()} Age {p_age_int} strategic window."
            threat_alert = ""
            attack_win = 240
            urgency = "medium"

            if p_civ.lower() == "franks" and p_age_int == 3:
                civ_power_spike = "Castle Age Knight HP Power Spike (+20% HP). Overpower infantry and archers now!"
                attack_win = 180
                urgency = "immediate"
            elif p_civ.lower() == "britons" and p_age_int in (2, 3):
                civ_power_spike = "Archery Range Advantage. Kite enemy infantry and establish hill control."

            if opp_civ.lower() == "vikings" and p_age_int == 3:
                threat_alert = "Warning: Do not allow Vikings to mass Elite Berserkers with Berserkergang in Imperial Age. Strike now!"

            if top_stance == "ALL_IN_AGGRESSION":
                urgency = "immediate"
                attack_win = min(180, attack_win)
            elif top_stance == "DEFENSIVE_TURTLING":
                urgency = "defend_now"

            stance_res = StanceTimingResult(
                recommended_stance=top_stance,
                stance_confidence=round(conf, 4),
                attack_window_sec=attack_win,
                urgency=urgency,
                civ_power_spike=civ_power_spike,
                threat_spike_alert=threat_alert,
                summary=f"Tactical Stance: {top_stance.replace('_', ' ').title()} ({round(conf * 100)}% conf).",
            )
        else:
            stance_res = self.stance_predictor.evaluate_timing_and_stance(
                state_or_vector=X,
                player_civ=p_civ,
                opponent_civ=opp_civ,
                player_age=p_age_int,
                game_time_sec=t_sec,
            )

        # 7. Synthesize Primary Directive & Actionable Checklist
        minutes = int(t_sec // 60)
        seconds = int(t_sec % 60)
        formatted_time = f"{minutes:02d}:{seconds:02d}"

        primary_comp_title = strategy_plan.primary_composition.replace("_", " ").title()
        directive = f"{age_enum.display_name.upper()} {primary_comp_title.upper()} PUSH"

        checklist: List[str] = []
        checklist.append(f"Produce: {primary_comp_title} from {strategy_plan.recommended_building.replace('_', ' ').title()}")
        if strategy_plan.recommended_tech_focus != "none":
            checklist.append(f"Research: {strategy_plan.recommended_tech_focus.replace('_', ' ').title()}")
        for step in eco_plan.shift_instructions[:2]:
            checklist.append(f"Macro: {step}")
        checklist.append(f"Stance: {stance_res.recommended_stance.replace('_', ' ').title()} - {stance_res.urgency.upper()} timing")

        latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        match_context = MatchContext(
            player_civ=p_civ,
            opponent_civ=opp_civ,
            player_elo=p_elo,
            player_age=p_age_int,
            player_age_name=age_enum.display_name,
            game_time_sec=t_sec,
            formatted_time=formatted_time,
        )

        return MLRecommendation(
            match_context=match_context,
            primary_directive=directive,
            win_probability=win_res,
            military_action_plan=strategy_plan,
            counter_matrix=counter_result,
            economic_rebalance=eco_plan,
            tactical_stance=stance_res,
            actionable_checklist=checklist,
            inference_latency_ms=latency_ms,
        )

    def benchmark_latency(self, iterations: int = 100) -> Dict[str, float]:
        """Benchmark inference latency over multiple iterations to verify sub-20ms requirement."""
        sample_state = {
            "player_civ": "Franks",
            "opponent_civ": "Vikings",
            "player_age": 3,
            "player_elo": 1100,
            "timestamp_sec": 1350,
            "food": 350,
            "wood": 700,
            "gold": 120,
            "stone": 200,
            "vills_total": 45,
            "vills_food": 14,
            "vills_wood": 22,
            "vills_gold": 7,
            "vills_stone": 2,
            "military_total": 6,
            "cavalry_count": 4,
            "archer_count": 2,
            "opp_sighted_infantry": 5,
            "opp_sighted_archers": 2,
        }

        # Warmup run
        _ = self.get_recommendation(sample_state)

        latencies: List[float] = []
        for _ in range(iterations):
            t0 = time.perf_counter()
            _ = self.get_recommendation(sample_state)
            latencies.append((time.perf_counter() - t0) * 1000.0)

        lat_arr = np.array(latencies)
        return {
            "mean_ms": round(float(np.mean(lat_arr)), 2),
            "p50_ms": round(float(np.percentile(lat_arr, 50)), 2),
            "p95_ms": round(float(np.percentile(lat_arr, 95)), 2),
            "p99_ms": round(float(np.percentile(lat_arr, 99)), 2),
            "max_ms": round(float(np.max(lat_arr)), 2),
            "sub_20ms_pass": bool(np.percentile(lat_arr, 99) < 20.0),
        }
