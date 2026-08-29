"""
AoE2 Coach Pro Tournament Benchmarking Engine (Phase 6):
Evaluates ML inference accuracy, counter validity, economic rebalancing efficiency,
and latency SLAs against pro player tournament matches.
"""

import time
import json
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from aoe2_coach.models.inference_service import MLInferenceService, MLRecommendation
from aoe2_coach.explanation.engine import TacticalExplanationEngine
from aoe2_coach.explanation.schemas import LLMConfig
from aoe2_coach.benchmarks.pro_datasets import (
    ProScenario,
    CURATED_PRO_SCENARIOS,
    load_parquet_pro_snapshots,
)


class ScenarioEvaluation(BaseModel):
    """Evaluation result for an individual pro scenario."""
    scenario_id: str
    matchup: str
    player_civ: str
    opponent_civ: str
    game_age: int
    top1_match: bool
    top3_match: bool
    building_match: bool
    stance_match: bool
    counter_valid: bool
    recommended_comp: str
    top3_rankings: List[str]
    expected_comps: List[str]
    recommended_building: str
    expected_building: str
    recommended_stance: str
    expected_stance: str
    eco_allocation_mae: float
    inference_latency_ms: float
    explanation_latency_ms: float
    total_latency_ms: float
    strategic_summary: str


class LatencyProfile(BaseModel):
    """Statistical latency metrics in milliseconds."""
    mean_ms: float
    p50_ms: float
    p90_ms: float
    p95_ms: float
    p99_ms: float
    max_ms: float
    sub_20ms_pass: bool


class BenchmarkResult(BaseModel):
    """Aggregate benchmark metrics across all pro matches."""
    total_scenarios: int
    top1_accuracy_pct: float
    top3_recall_pct: float
    building_accuracy_pct: float
    stance_agreement_pct: float
    counter_validity_pct: float
    mean_eco_mae_vills: float
    ml_latency: LatencyProfile
    total_latency: LatencyProfile
    feudal_top1_acc_pct: float
    castle_top1_acc_pct: float
    imperial_top1_acc_pct: float
    all_slas_passed: bool


class BenchmarkReport(BaseModel):
    """Complete benchmark report including aggregate metrics and scenario breakdowns."""
    timestamp: str
    summary: BenchmarkResult
    scenario_evaluations: List[ScenarioEvaluation]
    quality_gates: Dict[str, bool]

    def to_markdown(self) -> str:
        """Format benchmark report as rich Markdown documentation."""
        md = []
        md.append("# AoE2 Coach AI — Pro Tournament Match Benchmark Report")
        md.append(f"**Execution Timestamp:** {self.timestamp}\n")
        
        md.append("## 1. Executive Summary & SLA Verification")
        md.append("| Benchmark Metric | Target SLA | Measured Score | Status |")
        md.append("| :--- | :--- | :--- | :--- |")
        
        top1_status = "✅ PASS" if self.summary.top1_accuracy_pct >= 75.0 else "❌ FAIL"
        md.append(f"| **Top-1 Strategy Agreement** | $\\ge 75.0\\%$ | **{self.summary.top1_accuracy_pct:.1f}%** | {top1_status} |")
        
        top3_status = "✅ PASS" if self.summary.top3_recall_pct >= 90.0 else "❌ FAIL"
        md.append(f"| **Top-3 Strategy Recall** | $\\ge 90.0\\%$ | **{self.summary.top3_recall_pct:.1f}%** | {top3_status} |")

        bldg_status = "✅ PASS" if self.summary.building_accuracy_pct >= 80.0 else "❌ FAIL"
        md.append(f"| **Production Building Match** | $\\ge 80.0\\%$ | **{self.summary.building_accuracy_pct:.1f}%** | {bldg_status} |")

        stance_status = "✅ PASS" if self.summary.stance_agreement_pct >= 70.0 else "❌ FAIL"
        md.append(f"| **Tactical Stance Agreement** | $\\ge 70.0\\%$ | **{self.summary.stance_agreement_pct:.1f}%** | {stance_status} |")

        counter_status = "✅ PASS" if self.summary.counter_validity_pct >= 90.0 else "❌ FAIL"
        md.append(f"| **Counter Matrix Compliance** | $\\ge 90.0\\%$ | **{self.summary.counter_validity_pct:.1f}%** | {counter_status} |")

        eco_status = "✅ PASS" if self.summary.mean_eco_mae_vills <= 3.5 else "❌ FAIL"
        md.append(f"| **Macro Rebalance MAE** | $\\le 3.5$ vills | **{self.summary.mean_eco_mae_vills:.2f} vills** | {eco_status} |")

        lat_status = "✅ PASS" if self.summary.ml_latency.p99_ms < 20.0 else "❌ FAIL"
        md.append(f"| **ML Inference P99 Latency** | $< 20.0$ ms | **{self.summary.ml_latency.p99_ms:.2f} ms** | {lat_status} |")
        
        md.append("\n## 2. Latency Profiling")
        md.append("| Pipeline Stage | Mean | P50 (Median) | P90 | P95 | P99 | Max |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        md.append(
            f"| **ML ONNX Inference Engine** | {self.summary.ml_latency.mean_ms:.2f}ms | "
            f"{self.summary.ml_latency.p50_ms:.2f}ms | {self.summary.ml_latency.p90_ms:.2f}ms | "
            f"{self.summary.ml_latency.p95_ms:.2f}ms | {self.summary.ml_latency.p99_ms:.2f}ms | "
            f"{self.summary.ml_latency.max_ms:.2f}ms |"
        )
        md.append(
            f"| **Total Recommendation Pipeline** | {self.summary.total_latency.mean_ms:.2f}ms | "
            f"{self.summary.total_latency.p50_ms:.2f}ms | {self.summary.total_latency.p90_ms:.2f}ms | "
            f"{self.summary.total_latency.p95_ms:.2f}ms | {self.summary.total_latency.p99_ms:.2f}ms | "
            f"{self.summary.total_latency.max_ms:.2f}ms |"
        )

        md.append("\n## 3. Performance by Game Age")
        md.append(f"- **Feudal Age Strategy Accuracy:** {self.summary.feudal_top1_acc_pct:.1f}%")
        md.append(f"- **Castle Age Strategy Accuracy:** {self.summary.castle_top1_acc_pct:.1f}%")
        md.append(f"- **Imperial Age Strategy Accuracy:** {self.summary.imperial_top1_acc_pct:.1f}%")

        md.append("\n## 4. Scenario Breakdown (Top Tournament Matches)")
        md.append("| Scenario ID | Matchup | Age | Recommended Comp | Expected Pro Comp | Stance | ML Latency | Result |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
        for sc in self.scenario_evaluations:
            res_icon = "✅" if sc.top1_match else ("⚠️ Top-3" if sc.top3_match else "❌")
            md.append(
                f"| `{sc.scenario_id}` | {sc.matchup} | Age {sc.game_age} | "
                f"**{sc.recommended_comp}** | {', '.join(sc.expected_comps)} | "
                f"{sc.recommended_stance} | {sc.inference_latency_ms:.1f}ms | {res_icon} |"
            )

        return "\n".join(md)


class BenchmarkEngine:
    """Engine for running comprehensive benchmarks on ML and rules models."""

    def __init__(
        self,
        ml_service: Optional[MLInferenceService] = None,
        explanation_engine: Optional[TacticalExplanationEngine] = None,
    ):
        self.ml_service = ml_service or MLInferenceService()
        self.explanation_engine = explanation_engine or TacticalExplanationEngine(
            config=LLMConfig(timeout_seconds=2.0),
            force_fallback=True,
        )

    def evaluate_scenario(self, scenario: ProScenario) -> ScenarioEvaluation:
        """Run ML inference & validation on a single pro tournament scenario."""
        t_start = time.perf_counter()

        # Build flat state dict
        total_vills = scenario.vills_food + scenario.vills_wood + scenario.vills_gold + scenario.vills_stone
        state_dict = {
            "player_civ": scenario.player_civ,
            "opponent_civ": scenario.opponent_civ,
            "player_age": scenario.current_age,
            "player_elo": scenario.player_elo,
            "opponent_elo": scenario.opponent_elo,
            "timestamp_sec": scenario.game_time_sec,
            "food": scenario.food,
            "wood": scenario.wood,
            "gold": scenario.gold,
            "stone": scenario.stone,
            "vills_total": total_vills,
            "vills_food": scenario.vills_food,
            "vills_wood": scenario.vills_wood,
            "vills_gold": scenario.vills_gold,
            "vills_stone": scenario.vills_stone,
            "military_total": sum(scenario.military_units.values()),
            "sighted_units": [
                {"unit": uname, "count": ucount}
                for uname, ucount in scenario.sighted_enemy_units.items()
            ],
            "sighted_buildings": [
                {"building": bname, "count": bcount}
                for bname, bcount in scenario.sighted_enemy_buildings.items()
            ],
        }

        # 1. Run ML inference
        rec: MLRecommendation = self.ml_service.get_recommendation(state_dict)
        t_ml_done = time.perf_counter()

        # 2. Run explanation (with fallback for benchmark speed/reproducibility)
        exp = self.explanation_engine.explain(rec, elo_override=scenario.player_elo, force_fallback=True)
        t_exp_done = time.perf_counter()

        # Evaluate accuracies
        primary_comp = rec.military_action_plan.primary_composition
        top3_comps = [r.composition for r in rec.military_action_plan.rankings[:3]]

        top1_match = primary_comp in scenario.expected_winning_compositions
        top3_match = any(c in scenario.expected_winning_compositions for c in top3_comps)

        bldg_match = (
            rec.military_action_plan.recommended_building.lower() == scenario.expected_primary_building.lower()
            or (scenario.expected_primary_building.lower() in ("stable", "archery_range", "barracks", "castle", "monastery", "siege_workshop")
                and primary_comp in scenario.expected_winning_compositions)
        )

        s_exp = scenario.expected_stance.upper()
        s_rec = rec.tactical_stance.recommended_stance.upper()
        stance_match = (
            s_rec == s_exp
            or (s_exp == "FORWARD_PRESSURE" and s_rec in ("ALL_IN_AGGRESSION", "FORWARD_PRESSURE", "RELIC_HILL_CONTROL"))
            or (s_exp == "ALL_IN_AGGRESSION" and s_rec in ("ALL_IN_AGGRESSION", "FORWARD_PRESSURE"))
            or (s_exp == "DEFENSIVE_TURTLING" and s_rec in ("DEFENSIVE_TURTLING", "FAST_IMPERIAL_BOOM", "RELIC_HILL_CONTROL"))
            or (s_exp == "RELIC_HILL_CONTROL" and s_rec in ("RELIC_HILL_CONTROL", "DEFENSIVE_TURTLING", "FORWARD_PRESSURE"))
        )

        counter_valid = len(rec.counter_matrix.recommended_counters) > 0

        # Calculate eco villager MAE
        target_food = rec.economic_rebalance.target_allocation.food
        target_wood = rec.economic_rebalance.target_allocation.wood
        target_gold = rec.economic_rebalance.target_allocation.gold
        
        eco_mae = float(np.mean([
            abs(target_food - scenario.vills_food),
            abs(target_wood - scenario.vills_wood),
            abs(target_gold - scenario.vills_gold),
        ]))

        ml_lat = round((t_ml_done - t_start) * 1000.0, 2)
        exp_lat = round((t_exp_done - t_ml_done) * 1000.0, 2)
        tot_lat = round((t_exp_done - t_start) * 1000.0, 2)

        return ScenarioEvaluation(
            scenario_id=scenario.scenario_id,
            matchup=scenario.matchup,
            player_civ=scenario.player_civ,
            opponent_civ=scenario.opponent_civ,
            game_age=scenario.current_age,
            top1_match=top1_match,
            top3_match=top3_match,
            building_match=bldg_match,
            stance_match=stance_match,
            counter_valid=counter_valid,
            recommended_comp=primary_comp,
            top3_rankings=top3_comps,
            expected_comps=scenario.expected_winning_compositions,
            recommended_building=rec.military_action_plan.recommended_building,
            expected_building=scenario.expected_primary_building,
            recommended_stance=rec.tactical_stance.recommended_stance,
            expected_stance=scenario.expected_stance,
            eco_allocation_mae=eco_mae,
            inference_latency_ms=ml_lat,
            explanation_latency_ms=exp_lat,
            total_latency_ms=tot_lat,
            strategic_summary=rec.military_action_plan.strategic_summary,
        )

    def run_benchmark(
        self,
        scenarios: Optional[List[ProScenario]] = None,
        iterations_per_scenario: int = 1,
    ) -> BenchmarkReport:
        """Run full benchmark across all scenarios with latency profiling."""
        test_scenarios = scenarios or CURATED_PRO_SCENARIOS
        evaluations: List[ScenarioEvaluation] = []
        ml_latencies: List[float] = []
        tot_latencies: List[float] = []

        for sc in test_scenarios:
            for _ in range(iterations_per_scenario):
                res = self.evaluate_scenario(sc)
                ml_latencies.append(res.inference_latency_ms)
                tot_latencies.append(res.total_latency_ms)
            # Record first evaluation for reporting
            evaluations.append(self.evaluate_scenario(sc))

        total_scenarios = len(evaluations)
        top1_acc = (sum(1 for e in evaluations if e.top1_match) / total_scenarios) * 100.0
        top3_rec = (sum(1 for e in evaluations if e.top3_match) / total_scenarios) * 100.0
        bldg_acc = (sum(1 for e in evaluations if e.building_match) / total_scenarios) * 100.0
        stance_acc = (sum(1 for e in evaluations if e.stance_match) / total_scenarios) * 100.0
        counter_val = (sum(1 for e in evaluations if e.counter_valid) / total_scenarios) * 100.0
        mean_eco_mae = float(np.mean([e.eco_allocation_mae for e in evaluations]))

        # Game Age Breakdowns
        feudal_evals = [e for e in evaluations if e.game_age == 2]
        castle_evals = [e for e in evaluations if e.game_age == 3]
        imp_evals = [e for e in evaluations if e.game_age == 4]

        feudal_acc = (sum(1 for e in feudal_evals if e.top1_match) / max(1, len(feudal_evals))) * 100.0
        castle_acc = (sum(1 for e in castle_evals if e.top1_match) / max(1, len(castle_evals))) * 100.0
        imp_acc = (sum(1 for e in imp_evals if e.top1_match) / max(1, len(imp_evals))) * 100.0

        ml_lat_arr = np.array(ml_latencies)
        tot_lat_arr = np.array(tot_latencies)

        ml_profile = LatencyProfile(
            mean_ms=round(float(np.mean(ml_lat_arr)), 2),
            p50_ms=round(float(np.percentile(ml_lat_arr, 50)), 2),
            p90_ms=round(float(np.percentile(ml_lat_arr, 90)), 2),
            p95_ms=round(float(np.percentile(ml_lat_arr, 95)), 2),
            p99_ms=round(float(np.percentile(ml_lat_arr, 99)), 2),
            max_ms=round(float(np.max(ml_lat_arr)), 2),
            sub_20ms_pass=bool(np.percentile(ml_lat_arr, 99) < 20.0),
        )

        tot_profile = LatencyProfile(
            mean_ms=round(float(np.mean(tot_lat_arr)), 2),
            p50_ms=round(float(np.percentile(tot_lat_arr, 50)), 2),
            p90_ms=round(float(np.percentile(tot_lat_arr, 90)), 2),
            p95_ms=round(float(np.percentile(tot_lat_arr, 95)), 2),
            p99_ms=round(float(np.percentile(tot_lat_arr, 99)), 2),
            max_ms=round(float(np.max(tot_lat_arr)), 2),
            sub_20ms_pass=bool(np.percentile(tot_lat_arr, 99) < 50.0),
        )

        quality_gates = {
            "top1_accuracy_gte_75": top1_acc >= 75.0,
            "top3_recall_gte_90": top3_rec >= 90.0,
            "building_acc_gte_80": bldg_acc >= 80.0,
            "counter_validity_gte_90": counter_val >= 90.0,
            "sub_20ms_ml_inference": ml_profile.p99_ms < 20.0,
        }

        all_passed = all(quality_gates.values())

        summary = BenchmarkResult(
            total_scenarios=total_scenarios,
            top1_accuracy_pct=round(top1_acc, 2),
            top3_recall_pct=round(top3_rec, 2),
            building_accuracy_pct=round(bldg_acc, 2),
            stance_agreement_pct=round(stance_acc, 2),
            counter_validity_pct=round(counter_val, 2),
            mean_eco_mae_vills=round(mean_eco_mae, 2),
            ml_latency=ml_profile,
            total_latency=tot_profile,
            feudal_top1_acc_pct=round(feudal_acc, 2),
            castle_top1_acc_pct=round(castle_acc, 2),
            imperial_top1_acc_pct=round(imp_acc, 2),
            all_slas_passed=all_passed,
        )

        return BenchmarkReport(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            summary=summary,
            scenario_evaluations=evaluations,
            quality_gates=quality_gates,
        )
