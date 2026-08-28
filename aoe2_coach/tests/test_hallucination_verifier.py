"""
Unit tests for HallucinationVerifier and rule guardrails.
"""

import pytest
from aoe2_coach.models.inference_service import MLInferenceService
from aoe2_coach.explanation.schemas import (
    CoachingExplanation,
    TacticalMilitaryAdvice,
    TacticalEconomyAdvice,
    TacticalTimingAdvice,
    ELOTier,
)
from aoe2_coach.explanation.hallucination_verifier import HallucinationVerifier


@pytest.fixture
def franks_recommendation():
    service = MLInferenceService()
    state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "player_elo": 1100,
        "timestamp_sec": 1200,
        "food": 300,
        "wood": 600,
        "gold": 150,
        "stone": 100,
        "vills_total": 45,
        "vills_food": 15,
        "vills_wood": 20,
        "vills_gold": 8,
        "vills_stone": 2,
        "opp_sighted_infantry": 5,
    }
    return service.get_recommendation(state)


@pytest.fixture
def aztecs_recommendation():
    service = MLInferenceService()
    state = {
        "player_civ": "Aztecs",
        "opponent_civ": "Franks",
        "player_age": 3,
        "player_elo": 1200,
        "timestamp_sec": 1300,
        "food": 400,
        "wood": 500,
        "gold": 200,
        "stone": 100,
        "vills_total": 40,
        "vills_food": 16,
        "vills_wood": 14,
        "vills_gold": 8,
        "vills_stone": 2,
        "opp_sighted_cavalry": 6,
    }
    return service.get_recommendation(state)


def test_hallucination_verifier_valid_pass(franks_recommendation):
    explanation = CoachingExplanation(
        primary_directive="CASTLE AGE KNIGHT PUSH",
        coach_summary="Mass knights against infantry.",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Knight",
            secondary_unit_recommendation="Monk",
            production_building_instruction="Produce Knights from 3 Stables",
            key_tech_priorities=["Chain Barding Armor", "Husbandry"],
            counter_explanation="Knights overwhelm Viking infantry.",
            micro_positioning_tip="Patrol into engagements.",
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="Floating wood.",
            immediate_action="Move 6 woodcutters to farms.",
            target_villager_allocation={"food": 22, "wood": 12, "gold": 9, "stone": 2},
            macro_tip="Keep TC running.",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Aggressive Timing",
            attack_window="Next 3 minutes",
            threat_alert=None,
            strategic_spike_reasoning="Franks +20% HP spike",
        ),
        priority_checklist=["1. Train Knights", "2. Reseed Farms"],
    )

    result = HallucinationVerifier.verify_and_sanitize(explanation, franks_recommendation)
    assert result.is_valid is True
    assert len(result.violations) == 0
    assert result.sanitized_explanation.military_plan.primary_unit_recommendation == "Knight"


def test_hallucination_verifier_catches_illegal_cavalry_for_aztecs(aztecs_recommendation):
    # Aztecs CANNOT make Knights or Cavalry
    explanation = CoachingExplanation(
        primary_directive="CASTLE AGE CAVALRY PUSH",
        coach_summary="Mass Paladins and Knights.",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Knight",  # Aztec hallucination!
            secondary_unit_recommendation="Hussar", # Aztec hallucination!
            production_building_instruction="Build 3 Stables",
            key_tech_priorities=["Bloodlines"], # Aztec hallucination!
            counter_explanation="Knights fight enemy cavalry.",
            micro_positioning_tip=None,
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="Wood float.",
            immediate_action="Move vills.",
            target_villager_allocation={"food": 18, "wood": 12, "gold": 8, "stone": 2},
            macro_tip="Eco balance.",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Aggressive",
            attack_window="Now",
            threat_alert=None,
            strategic_spike_reasoning="None",
        ),
        priority_checklist=["1. Train Knights"],
    )

    result = HallucinationVerifier.verify_and_sanitize(explanation, aztecs_recommendation)
    assert result.is_valid is False
    assert any("not available to civilization 'Aztecs'" in v for v in result.violations)
    assert any("Bloodlines" in v for v in result.violations)

    # Verify auto-correction
    sanitized_primary = result.sanitized_explanation.military_plan.primary_unit_recommendation
    assert sanitized_primary != "Knight"
    assert sanitized_primary.lower() in ("pikeman", "spearman", "monk", "eagle_warrior", "jaguar_warrior")


def test_hallucination_verifier_catches_disabled_and_premature_techs(franks_recommendation):
    explanation = CoachingExplanation(
        primary_directive="KNIGHT PUSH",
        coach_summary="Summary",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Knight",
            production_building_instruction="Build Stables",
            key_tech_priorities=[
                "Bloodlines",          # Franks don't get bloodlines (they have passive civ bonus)
                "Plate Barding Armor", # Imperial tech while player is in Castle Age
                "Chain Barding Armor", # Valid Castle tech
            ],
            counter_explanation="Counters enemy",
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="None",
            immediate_action="None",
            target_villager_allocation={"food": 20, "wood": 14, "gold": 9, "stone": 2},
            macro_tip="Tip",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Posture",
            attack_window="3m",
            threat_alert=None,
            strategic_spike_reasoning="Reasoning",
        ),
        priority_checklist=["1. Action"],
    )

    result = HallucinationVerifier.verify_and_sanitize(explanation, franks_recommendation)
    assert result.is_valid is False
    assert any("Bloodlines" in v for v in result.violations)
    assert any("Plate Barding Armor" in v for v in result.violations)

    # The sanitized tech list must NOT have Bloodlines or Plate Barding Armor
    sanitized_techs = result.sanitized_explanation.military_plan.key_tech_priorities
    assert "Bloodlines" not in sanitized_techs
    assert "Plate Barding Armor" not in sanitized_techs
    assert "Chain Barding Armor" in sanitized_techs


def test_hallucination_verifier_catches_math_discrepancy(franks_recommendation):
    # Total vills is 45, but LLM hallucinates 15 total target vills
    explanation = CoachingExplanation(
        primary_directive="PUSH",
        coach_summary="Summary",
        elo_tier=ELOTier.INTERMEDIATE,
        military_plan=TacticalMilitaryAdvice(
            primary_unit_recommendation="Knight",
            production_building_instruction="Stables",
            key_tech_priorities=["Chain Barding Armor"],
            counter_explanation="Counters",
        ),
        economic_plan=TacticalEconomyAdvice(
            problem_diagnosis="Diagnosis",
            immediate_action="Action",
            target_villager_allocation={"food": 5, "wood": 5, "gold": 5, "stone": 0}, # Sum is only 15!
            macro_tip="Tip",
        ),
        timing_plan=TacticalTimingAdvice(
            posture="Posture",
            attack_window="3m",
            threat_alert=None,
            strategic_spike_reasoning="Reasoning",
        ),
        priority_checklist=[],
    )

    result = HallucinationVerifier.verify_and_sanitize(explanation, franks_recommendation)
    assert result.is_valid is False
    assert any("Economic math violation" in v for v in result.violations)

    # Sanity check target vill sum
    corrected_alloc = result.sanitized_explanation.economic_plan.target_villager_allocation
    corrected_sum = sum(corrected_alloc.values())
    assert abs(corrected_sum - 45) <= 2
    assert len(result.sanitized_explanation.priority_checklist) >= 2
