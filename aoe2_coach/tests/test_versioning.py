"""
Comprehensive Tests for Patch Version Isolation across Rules, Models, Explanations, and API.
"""

import pytest
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.rules.game_ruleset import RulesRegistry
from aoe2_coach.rules.damage_calculator import calculate_damage_breakdown
from aoe2_coach.rules.economy_solver import EconomySolver
from aoe2_coach.rules.tech_tree import is_unit_available, get_civ_info
from aoe2_coach.rules.units import get_unit_stats
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.model_registry import ModelRegistry
from aoe2_coach.models.inference_service import MatchContext, MLRecommendation
from aoe2_coach.explanation.schemas import (
    CoachingExplanation,
    ELOTier,
    TacticalMilitaryAdvice,
    TacticalEconomyAdvice,
    TacticalTimingAdvice,
)
from aoe2_coach.explanation.hallucination_verifier import HallucinationVerifier
from aoe2_coach.api.service import CoachAPIService
from aoe2_coach.api.schemas import SnapshotInput, CombatSimRequest


def test_rules_registry_versions():
    """Verify registry correctly resolves supported patches and aliases."""
    supported = RulesRegistry.list_supported_versions()
    assert "101.102.x" in supported
    assert "101.103.x" in supported

    r_latest = RulesRegistry.get("latest")
    assert r_latest.patch_version == "101.103.x"

    r_102 = RulesRegistry.get("101.102.x")
    assert r_102.patch_version == "101.102.x"
    assert r_102.num_civs == 45
    assert not r_102.is_civ_supported("jurchens")
    assert not r_102.is_civ_supported("khitans")
    assert not r_102.is_civ_supported("shu")

    r_103 = RulesRegistry.get("101.103.x")
    assert r_103.patch_version == "101.103.x"
    assert r_103.num_civs == 48
    assert r_103.is_civ_supported("jurchens")
    assert r_103.is_civ_supported("khitans")
    assert r_103.is_civ_supported("shu")


def test_mechanics_differences():
    """Verify gather rate and elevation bonus differences across patches."""
    r_102 = RulesRegistry.get("101.102.x")
    r_103 = RulesRegistry.get("101.103.x")

    assert r_102.base_gather_rates["food_farm"] == 0.35
    assert r_103.base_gather_rates["food_farm"] == 0.33

    assert r_102.elevation_advantage == 0.25
    assert r_103.elevation_advantage == 0.20

    # Damage on hill
    knight = get_unit_stats("knight")
    archer = get_unit_stats("archer")

    dmg_102 = calculate_damage_breakdown(
        attacker=knight,
        defender=archer,
        elevation="high",
        ruleset=r_102,
    )
    dmg_103 = calculate_damage_breakdown(
        attacker=knight,
        defender=archer,
        elevation="high",
        ruleset=r_103,
    )

    # Hill bonus in 101.102.x (+25%) is strictly greater than or equal to 101.103.x (+20%)
    assert dmg_102.elevation_multiplier == 1.25
    assert dmg_103.elevation_multiplier == 1.20
    assert dmg_102.net_damage_per_hit >= dmg_103.net_damage_per_hit


def test_tech_tree_unit_availability():
    """Verify patch 101.102.x rejects new units, while 101.103.x accepts them."""
    r_102 = RulesRegistry.get("101.102.x")
    r_103 = RulesRegistry.get("101.103.x")

    assert not is_unit_available("jurchens", "iron_pagoda", age=Age.CASTLE, ruleset=r_102)
    assert is_unit_available("jurchens", "iron_pagoda", age=Age.CASTLE, ruleset=r_103)
    assert not is_unit_available("franks", "iron_pagoda", age=Age.CASTLE, ruleset=r_103)

    assert not is_unit_available("khitans", "ordo_cavalry", age=Age.CASTLE, ruleset=r_102)
    assert is_unit_available("khitans", "ordo_cavalry", age=Age.CASTLE, ruleset=r_103)


def test_economy_solver_farm_nerf_impact():
    """Verify reduced farm gather rate (0.33 vs 0.35) calculates higher required farm villagers."""
    r_102 = RulesRegistry.get("101.102.x")
    r_103 = RulesRegistry.get("101.103.x")

    solver_102 = EconomySolver(ruleset=r_102)
    solver_103 = EconomySolver(ruleset=r_103)

    # Compute gather rate for farms under same tech
    rate_102 = solver_102.calculate_gather_rates(civ="franks", researched_techs=["wheelbarrow"])
    rate_103 = solver_103.calculate_gather_rates(civ="franks", researched_techs=["wheelbarrow"])

    assert rate_102.food_farm > rate_103.food_farm


def test_model_registry_and_encoder_isolation():
    """Verify ModelRegistry isolates instances and feature encoders per patch."""
    service_102 = ModelRegistry.get_service("101.102.x")
    service_103 = ModelRegistry.get_service("101.103.x")

    assert service_102.patch_version == "101.102.x"
    assert service_103.patch_version == "101.103.x"
    assert service_102 is not service_103

    assert service_102.encoder.num_features == 76
    assert service_103.encoder.num_features == 76

    # Test recommendation inference on both
    sample_102_state = {
        "player_civ": "Franks",
        "opponent_civ": "Britons",
        "player_elo": 1200,
        "current_age": 3,
        "game_time_minutes": 18.0,
        "food": 300,
        "wood": 300,
        "gold": 200,
        "stone": 50,
        "vills_food": 14,
        "vills_wood": 12,
        "vills_gold": 6,
        "vills_stone": 0,
        "military_total": 6,
        "patch_version": "101.102.x",
    }
    rec_102 = service_102.get_recommendation(sample_102_state)
    assert rec_102.match_context.patch_version == "101.102.x"

    sample_103_state = {
        "player_civ": "Jurchens",
        "opponent_civ": "Britons",
        "player_elo": 1200,
        "current_age": 3,
        "game_time_minutes": 18.0,
        "food": 300,
        "wood": 300,
        "gold": 200,
        "stone": 50,
        "vills_food": 14,
        "vills_wood": 12,
        "vills_gold": 6,
        "vills_stone": 0,
        "military_total": 6,
        "patch_version": "101.103.x",
    }
    rec_103 = service_103.get_recommendation(sample_103_state)
    assert rec_103.match_context.patch_version == "101.103.x"
    assert rec_103.match_context.player_civ == "Jurchens"


def test_hallucination_verifier_version_boundaries():
    """Verify HallucinationVerifier catches patch-invalid civs/units."""
    service_102 = ModelRegistry.get_service("101.102.x")
    service_103 = ModelRegistry.get_service("101.103.x")

    # Construct synthetic recommendation for Franks
    rec = service_102.get_recommendation({
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "current_age": 3,
        "player_elo": 1200,
        "game_time_minutes": 20.0,
    })

    alloc_102 = rec.economic_rebalance.target_allocation
    hallucinated_exp = CoachingExplanation(
        primary_directive="HEAVY CAVALRY ASSAULT",
        coach_summary="Build heavy cavalry.",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Iron Pagoda",
            production_building_instruction="Produce from Castle",
            key_tech_priorities=["Iron Casting"],
            counter_explanation="Strong heavy cavalry.",
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="Balanced",
            immediate_action="Maintain vills",
            target_villager_allocation={"food": alloc_102.food, "wood": alloc_102.wood, "gold": alloc_102.gold, "stone": alloc_102.stone},
            macro_tip="Keep TC running",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Castle Push",
            attack_window="Now",
            strategic_spike_reasoning="Castle spike",
        ),
        priority_checklist=["1. Train Iron Pagoda"],
    )

    # In 101.102.x: Iron Pagoda is invalid for Franks AND doesn't exist in patch
    v_res_102 = HallucinationVerifier.verify_and_sanitize(
        explanation=hallucinated_exp,
        recommendation=rec,
        patch_version="101.102.x",
    )
    assert not v_res_102.is_valid
    assert any("Iron Pagoda" in viol for viol in v_res_102.violations)
    assert v_res_102.sanitized_explanation.military_plan.primary_unit_recommendation != "Iron Pagoda"

    # In 101.103.x: for Jurchens, Iron Pagoda is a valid unique unit
    jurchen_rec = service_103.get_recommendation({
        "player_civ": "Jurchens",
        "opponent_civ": "Vikings",
        "current_age": 3,
        "player_elo": 1200,
        "game_time_minutes": 20.0,
        "patch_version": "101.103.x",
    })
    alloc_103 = jurchen_rec.economic_rebalance.target_allocation
    jurchen_exp = CoachingExplanation(
        primary_directive="JURCHEN ASSAULT",
        coach_summary="Build Iron Pagoda.",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Iron Pagoda",
            production_building_instruction="Produce from Castle",
            key_tech_priorities=["Iron Casting"],
            counter_explanation="Strong unique cavalry.",
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="Balanced",
            immediate_action="Maintain vills",
            target_villager_allocation={"food": alloc_103.food, "wood": alloc_103.wood, "gold": alloc_103.gold, "stone": alloc_103.stone},
            macro_tip="Keep TC running",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Castle Push",
            attack_window="Now",
            strategic_spike_reasoning="Castle spike",
        ),
        priority_checklist=["1. Train Iron Pagoda"],
    )
    v_res_103 = HallucinationVerifier.verify_and_sanitize(
        explanation=jurchen_exp,
        recommendation=jurchen_rec,
        patch_version="101.103.x",
    )
    assert v_res_103.is_valid
    assert v_res_103.sanitized_explanation.military_plan.primary_unit_recommendation == "Iron Pagoda"


def test_api_service_version_isolation():
    """Verify CoachAPIService handles multi-patch requests."""
    api = CoachAPIService()

    # Health endpoint returns supported patches
    health = api.check_health()
    assert "101.102.x" in health.supported_patches
    assert "101.103.x" in health.supported_patches
    assert health.active_patch == "101.103.x"

    # Recommendation for 101.102.x
    res_102 = api.generate_recommendation(
        SnapshotInput(
            player_civ="Franks",
            opponent_civ="Vikings",
            patch_version="101.102.x",
            force_fallback=True,
        )
    )
    assert res_102.patch_version == "101.102.x"

    # Recommendation for 101.103.x with new civ
    res_103 = api.generate_recommendation(
        SnapshotInput(
            player_civ="Jurchens",
            opponent_civ="Vikings",
            patch_version="101.103.x",
            force_fallback=True,
        )
    )
    assert res_103.patch_version == "101.103.x"
    assert res_103.match_context["player_civ"] == "Jurchens"
