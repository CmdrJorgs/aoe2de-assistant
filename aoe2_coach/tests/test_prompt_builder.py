"""
Unit tests for AoE2 PromptBuilder and ELO tier calibration.
"""

import json
import pytest
from aoe2_coach.models.inference_service import MLInferenceService
from aoe2_coach.explanation.schemas import ELOTier, get_elo_tier
from aoe2_coach.explanation.prompt_builder import PromptBuilder


def test_get_elo_tier():
    assert get_elo_tier(800) == ELOTier.BEGINNER
    assert get_elo_tier(999) == ELOTier.BEGINNER
    assert get_elo_tier(1000) == ELOTier.INTERMEDIATE
    assert get_elo_tier(1250) == ELOTier.INTERMEDIATE
    assert get_elo_tier(1399) == ELOTier.INTERMEDIATE
    assert get_elo_tier(1400) == ELOTier.ADVANCED
    assert get_elo_tier(2000) == ELOTier.ADVANCED
    assert get_elo_tier(None) == ELOTier.BEGINNER


def test_system_prompt_elo_calibration():
    beginner_prompt = PromptBuilder.build_system_prompt(elo=850)
    assert "BEGINNER (< 1000 ELO)" in beginner_prompt
    assert "MACRO fundamentals" in beginner_prompt

    intermediate_prompt = PromptBuilder.build_system_prompt(elo=1200)
    assert "INTERMEDIATE (1000 - 1400 ELO)" in intermediate_prompt
    assert "power spikes" in intermediate_prompt

    advanced_prompt = PromptBuilder.build_system_prompt(elo=1700)
    assert "ADVANCED (> 1400 ELO)" in advanced_prompt
    assert "micro positioning" in advanced_prompt.lower() or "micro" in advanced_prompt.lower()


def test_build_user_prompt_structure():
    service = MLInferenceService()
    state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "player_elo": 1150,
        "timestamp_sec": 1200,
        "food": 320,
        "wood": 750,
        "gold": 120,
        "stone": 450,
        "vills_total": 48,
        "vills_food": 14,
        "vills_wood": 26,
        "vills_gold": 6,
        "vills_stone": 2,
        "sighted_units": [{"unit": "berserk", "count": 5}],
    }
    rec = service.get_recommendation(state)

    user_prompt = PromptBuilder.build_user_prompt(rec, user_notes="Enemy forward castle spotted near gold")
    assert "Franks" in user_prompt
    assert "Vikings" in user_prompt
    assert "Enemy forward castle spotted near gold" in user_prompt
    assert "ml_strategic_prediction" in user_prompt
    assert "economic_rebalancer" in user_prompt
    assert "threat_analysis" in user_prompt
