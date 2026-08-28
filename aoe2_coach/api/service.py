"""
AoE2 Coach API Service Layer:
Orchestrates ML inference, rules evaluation, LLM explanations, and combat simulations.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from aoe2_coach.schemas.game_constants import (
    Age,
    CIVILIZATIONS,
    CIV_NAME_TO_ID,
    get_civ_name,
)
from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    SightedEntity,
    ResourceStockpile,
    VillagerAllocation,
    TargetLabels,
)
from aoe2_coach.models.inference_service import MLInferenceService, MLRecommendation
from aoe2_coach.explanation.engine import TacticalExplanationEngine
from aoe2_coach.explanation.schemas import LLMConfig
from aoe2_coach.rules.counter_matrix import CounterMatrixEngine
from aoe2_coach.rules.economy_solver import EconomySolver
from aoe2_coach.rules.tech_tree import get_civ_info, get_all_civs
from aoe2_coach.rules.units import UNITS_DATABASE, get_unit_stats
from aoe2_coach.rules.damage_calculator import calculate_damage_breakdown, simulate_duel
from aoe2_coach.api.schemas import (
    SnapshotInput,
    RecommendationResponse,
    CounterMatrixRequest,
    CounterMatrixResponse,
    EconomySolverRequest,
    EconomySolverResponse,
    CombatSimRequest,
    CombatSimResponse,
    HealthResponse,
)

logger = logging.getLogger(__name__)


def resolve_civ_id(civ_input: str) -> int:
    """Resolve civ string name or int to valid civ ID."""
    if isinstance(civ_input, int):
        return civ_input if civ_input in CIVILIZATIONS else 1
    if str(civ_input).isdigit():
        cid = int(civ_input)
        return cid if cid in CIVILIZATIONS else 1
    clean = str(civ_input).strip().lower()
    return CIV_NAME_TO_ID.get(clean, 1)


def snapshot_input_to_game_snapshot(inp: SnapshotInput) -> GameSnapshot:
    """Convert API SnapshotInput into domain GameSnapshot object."""
    p_civ_id = resolve_civ_id(inp.player_civ)
    p_civ_name = get_civ_name(p_civ_id)
    
    o_civ_id = resolve_civ_id(inp.opponent_civ)
    o_civ_name = get_civ_name(o_civ_id)
    
    vills_total = inp.vills_total or (inp.vills_food + inp.vills_wood + inp.vills_gold + inp.vills_stone)
    game_time_sec = int(inp.game_time_minutes * 60)
    
    player_state = PlayerState(
        player_id=1,
        civ_id=p_civ_id,
        civ_name=p_civ_name,
        elo=inp.player_elo,
        age=inp.current_age,
        age_name=f"Age {inp.current_age}",
        resources=ResourceStockpile(
            food=inp.food,
            wood=inp.wood,
            gold=inp.gold,
            stone=inp.stone,
        ),
        villagers=VillagerAllocation(
            total=vills_total,
            food=inp.vills_food,
            wood=inp.vills_wood,
            gold=inp.vills_gold,
            stone=inp.vills_stone,
        ),
        military_units=inp.military_units,
        buildings=inp.player_buildings,
        completed_techs=inp.completed_techs,
    )
    
    # Sighted entities
    sighted_units: List[SightedEntity] = []
    for uname, ucount in inp.sighted_enemy_units.items():
        sighted_units.append(
            SightedEntity(
                entity_name=uname,
                entity_type="unit",
                count=ucount,
                last_seen_sec=float(max(0, game_time_sec - 15)),
            )
        )
        
    sighted_bldgs: List[SightedEntity] = []
    for bname, bcount in inp.sighted_enemy_buildings.items():
        sighted_bldgs.append(
            SightedEntity(
                entity_name=bname,
                entity_type="building",
                count=bcount,
                last_seen_sec=float(max(0, game_time_sec - 30)),
            )
        )
        
    opp_age = inp.opponent_estimated_age or inp.current_age
    opponent_state = OpponentObservedState(
        civ_id=o_civ_id,
        civ_name=o_civ_name,
        estimated_age=opp_age,
        estimated_age_name=f"Age {opp_age}",
        sighted_units=sighted_units,
        sighted_buildings=sighted_bldgs,
    )
    
    return GameSnapshot(
        match_id="web-session",
        patch_version="101.102.x",
        timestamp_sec=game_time_sec,
        map_type="Arabia",
        player=player_state,
        opponent_observed=opponent_state,
        label=TargetLabels(winner=True),
    )


class CoachAPIService:
    """Singleton service manager for AoE2 Coach API."""

    def __init__(self, llm_config: Optional[LLMConfig] = None):
        self.ml_service = MLInferenceService()
        self.counter_engine = CounterMatrixEngine()
        self.economy_solver = EconomySolver()
        self.llm_config = llm_config or LLMConfig(
            base_url="http://127.0.0.1:8081/v1",
            model="qwen3.8-4b",
            api_key="llama.cpp",
            timeout_seconds=4.0,
        )
        self.explanation_engine = TacticalExplanationEngine(config=self.llm_config)

    def check_health(self) -> HealthResponse:
        """Check system status."""
        onnx_ready = bool(self.ml_service.onnx_engine and self.ml_service.onnx_engine.is_loaded)
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            onnx_loaded=onnx_ready,
            llm_connected=True,
            civs_count=len(CIVILIZATIONS),
            units_count=len(UNITS_DATABASE),
        )

    def generate_recommendation(self, input_data: SnapshotInput) -> RecommendationResponse:
        """
        Run end-to-end tactical recommendation:
        Snapshot -> ML Inference -> Rules Validation -> LLM Tactical Explanation.
        """
        t_start = time.perf_counter()
        
        # 1. Convert snapshot
        snapshot = snapshot_input_to_game_snapshot(input_data)
        
        # 2. Run ML + Rules inference
        ml_rec = self.ml_service.get_recommendation(snapshot)
        t_ml_done = time.perf_counter()
        ml_latency = round((t_ml_done - t_start) * 1000.0, 2)
        
        # 3. Run verified tactical explanation
        verified_resp = self.explanation_engine.explain(
            recommendation=ml_rec,
            elo_override=input_data.player_elo,
            user_notes=input_data.user_notes,
            force_fallback=input_data.force_fallback,
        )
        t_exp_done = time.perf_counter()
        exp_latency = round((t_exp_done - t_ml_done) * 1000.0, 2)
        total_latency = round((t_exp_done - t_start) * 1000.0, 2)
        
        return RecommendationResponse(
            match_context=ml_rec.match_context.model_dump(),
            primary_directive=verified_resp.explanation.primary_directive or ml_rec.primary_directive,
            win_probability=ml_rec.win_probability.model_dump(),
            military_action_plan=ml_rec.military_action_plan.model_dump(),
            counter_matrix=ml_rec.counter_matrix.model_dump(),
            economic_rebalance=ml_rec.economic_rebalance.model_dump(),
            tactical_stance=ml_rec.tactical_stance.model_dump(),
            actionable_checklist=verified_resp.explanation.priority_checklist or ml_rec.actionable_checklist,
            explanation=verified_resp.model_dump(),
            inference_latency_ms=ml_latency,
            explanation_latency_ms=exp_latency,
            total_latency_ms=total_latency,
        )

    def compute_counter_matrix(self, req: CounterMatrixRequest) -> CounterMatrixResponse:
        """Compute counter recommendations against specified enemy army."""
        age_enum = Age(req.current_age) if req.current_age in (1, 2, 3, 4) else Age.CASTLE
        
        res = self.counter_engine.recommend_counters(
            player_civ=req.player_civ,
            player_age=age_enum,
            enemy_units=req.enemy_army,
        )
        
        threat_dict = res.threat_analysis.model_dump()
        counters_list = [c.model_dump() for c in res.recommended_counters]
        
        return CounterMatrixResponse(
            player_civ=req.player_civ,
            current_age=req.current_age,
            threat_analysis=[threat_dict],
            recommended_counters=counters_list,
            counter_compositions=[{
                "primary": res.primary_unit_recommendation,
                "secondary": res.secondary_support_unit,
                "building": res.production_building_target,
                "summary": res.tactical_summary,
            }],
        )

    def solve_economy(self, req: EconomySolverRequest) -> EconomySolverResponse:
        """Compute exact villager allocation for given military goals."""
        target_prod = {g.unit_name.lower(): g.building_count for g in req.production_goals}
        
        cur_vills_dict = req.current_vills or {"food": 16, "wood": 14, "gold": 6, "stone": 2}
        total_v = sum(cur_vills_dict.values())
        cur_alloc = VillagerAllocation(
            total=total_v,
            food=cur_vills_dict.get("food", 0),
            wood=cur_vills_dict.get("wood", 0),
            gold=cur_vills_dict.get("gold", 0),
            stone=cur_vills_dict.get("stone", 0),
        )
        
        cur_stockpile_dict = req.current_stockpile or {"food": 200, "wood": 200, "gold": 100, "stone": 50}
        stockpile = ResourceStockpile(
            food=cur_stockpile_dict.get("food", 0),
            wood=cur_stockpile_dict.get("wood", 0),
            gold=cur_stockpile_dict.get("gold", 0),
            stone=cur_stockpile_dict.get("stone", 0),
        )
        
        res = self.economy_solver.solve_economy_balance(
            current_vills=cur_alloc,
            current_stockpile=stockpile,
            target_production=target_prod,
            researched_techs=req.researched_upgrades,
            civ=req.civ,
        )
        
        return EconomySolverResponse(
            target_food_vills=res.optimal_allocation.food,
            target_wood_vills=res.optimal_allocation.wood,
            target_gold_vills=res.optimal_allocation.gold,
            target_stone_vills=res.optimal_allocation.stone,
            total_target_vills=res.optimal_allocation.total,
            resource_generation_rates={
                "food": res.current_generation_rates.food_per_sec,
                "wood": res.current_generation_rates.wood_per_sec,
                "gold": res.current_generation_rates.gold_per_sec,
                "stone": res.current_generation_rates.stone_per_sec,
            },
            resource_consumption_rates={
                "food": res.production_demand_rates.food_per_sec,
                "wood": res.production_demand_rates.wood_per_sec,
                "gold": res.production_demand_rates.gold_per_sec,
                "stone": res.production_demand_rates.stone_per_sec,
            },
            net_rates={
                "food": res.net_resource_balance_rates.food_per_sec,
                "wood": res.net_resource_balance_rates.wood_per_sec,
                "gold": res.net_resource_balance_rates.gold_per_sec,
                "stone": res.net_resource_balance_rates.stone_per_sec,
            },
            delta_shifts=res.allocation_deltas,
            action_advice=res.actionable_rebalance_steps or [res.summary],
        )

    def simulate_combat(self, req: CombatSimRequest) -> CombatSimResponse:
        """Run combat simulation between two unit lines."""
        unit_a = get_unit_stats(req.attacker_unit.lower()) or list(UNITS_DATABASE.values())[0]
        unit_b = get_unit_stats(req.defender_unit.lower()) or list(UNITS_DATABASE.values())[1]
        
        elev_str = "high" if req.elevation_diff > 0 else ("low" if req.elevation_diff < 0 else "flat")
        
        dmg_a_to_b = calculate_damage_breakdown(
            attacker=unit_a,
            defender=unit_b,
            elevation=elev_str,
            attacker_civ=req.attacker_civ,
            defender_civ=req.defender_civ,
        )
        
        dmg_b_to_a = calculate_damage_breakdown(
            attacker=unit_b,
            defender=unit_a,
            elevation="low" if req.elevation_diff > 0 else ("high" if req.elevation_diff < 0 else "flat"),
            attacker_civ=req.defender_civ,
            defender_civ=req.attacker_civ,
        )
        
        duel = simulate_duel(
            unit1=unit_a,
            unit2=unit_b,
            unit1_techs=req.attacker_upgrades,
            unit2_techs=req.defender_upgrades,
            unit1_civ=req.attacker_civ,
            unit2_civ=req.defender_civ,
            elevation=elev_str,
        )
        
        # Calculate army engagement estimates
        total_dps_a = (dmg_a_to_b.dps) * req.attacker_count
        total_dps_b = (dmg_b_to_a.dps) * req.defender_count
        
        total_hp_a = unit_a.hp * req.attacker_count
        total_hp_b = unit_b.hp * req.defender_count
        
        time_a_kills_b = total_hp_b / max(0.1, total_dps_a)
        time_b_kills_a = total_hp_a / max(0.1, total_dps_b)
        
        if time_a_kills_b < time_b_kills_a:
            winner_name = unit_a.name
            rem_pct = max(0.1, 1.0 - (time_a_kills_b / max(0.1, time_b_kills_a)))
            surv_a = max(1, int(req.attacker_count * rem_pct))
            surv_b = 0
            duration = time_a_kills_b
        else:
            winner_name = unit_b.name
            rem_pct = max(0.1, 1.0 - (time_b_kills_a / max(0.1, time_a_kills_b)))
            surv_a = 0
            surv_b = max(1, int(req.defender_count * rem_pct))
            duration = time_b_kills_a
            
        summary = (
            f"{winner_name} wins mass engagement in {duration:.1f}s. "
            f"Remaining: {surv_a} {unit_a.name} vs {surv_b} {unit_b.name}. {duel.explanation}"
        )
        
        return CombatSimResponse(
            attacker_unit=unit_a.name,
            attacker_count=req.attacker_count,
            defender_unit=unit_b.name,
            defender_count=req.defender_count,
            single_hit_attacker_to_defender=int(dmg_a_to_b.net_damage_per_hit),
            single_hit_defender_to_attacker=int(dmg_b_to_a.net_damage_per_hit),
            simulated_winner=winner_name,
            time_to_kill_seconds=round(duration, 1),
            remaining_attackers=surv_a,
            remaining_defenders=surv_b,
            cost_efficiency_ratio=duel.cost_efficiency,
            tactical_summary=summary,
        )

    def get_civ_list(self) -> List[Dict[str, Any]]:
        """Get all civilizations with details."""
        res = []
        for name, cid in sorted(CIV_NAME_TO_ID.items(), key=lambda x: x[1]):
            civ_name = get_civ_name(cid)
            info = get_civ_info(civ_name)
            res.append({
                "id": cid,
                "name": civ_name,
                "architecture": info.architecture if info else "western_europe",
                "bonuses": info.civ_bonuses if info else [],
                "unique_units": info.unique_units if info else [],
                "castle_unique_tech": info.castle_unique_tech if info else None,
                "imperial_unique_tech": info.imperial_unique_tech if info else None,
                "team_bonus": info.team_bonus if info else "",
            })
        return res

    def get_unit_catalog(self) -> List[Dict[str, Any]]:
        """Get full unit catalog."""
        res = []
        for u in UNITS_DATABASE.values():
            res.append({
                "id": u.id,
                "name": u.name,
                "category": u.category,
                "age": u.age.value,
                "hp": u.hp,
                "attack": u.base_attack,
                "melee_armor": u.base_armor_melee,
                "pierce_armor": u.base_armor_pierce,
                "range": u.range,
                "reload_time": u.reload_time,
                "train_time": u.train_time_sec,
                "cost": {
                    "food": u.cost.food,
                    "wood": u.cost.wood,
                    "gold": u.cost.gold,
                    "stone": u.cost.stone,
                    "total": u.cost.total,
                },
            })
        return res
