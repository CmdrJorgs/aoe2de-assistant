"""
Unit and integration tests for TacticalExplanationEngine and DeterministicFallbackExplainer.
"""

import json
import pytest
from unittest.mock import MagicMock, patch

from aoe2_coach.models.inference_service import MLInferenceService
from aoe2_coach.explanation.schemas import (
    ELOTier,
    LLMConfig,
    VerifiedCoachingResponse,
    CoachingExplanation,
)
from aoe2_coach.explanation.fallback_engine import DeterministicFallbackExplainer
from aoe2_coach.explanation.engine import TacticalExplanationEngine
from aoe2_coach.explanation.client import OpenAICompatibleLLMClient


@pytest.fixture
def sample_match_recommendation():
    service = MLInferenceService()
    state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "player_elo": 950, # Beginner
        "timestamp_sec": 1260,
        "food": 320,
        "wood": 750,
        "gold": 120,
        "stone": 450,
        "vills_total": 48,
        "vills_food": 14,
        "vills_wood": 26,
        "vills_gold": 6,
        "vills_stone": 2,
        "opp_sighted_infantry": 5,
    }
    return service.get_recommendation(state)


def test_deterministic_fallback_explainer_beginner(sample_match_recommendation):
    explanation = DeterministicFallbackExplainer.generate_explanation(
        sample_match_recommendation,
        elo_tier_override=ELOTier.BEGINNER,
    )

    assert explanation.elo_tier == ELOTier.BEGINNER
    assert "CASTLE" in explanation.primary_directive
    assert explanation.military_plan.primary_unit_recommendation == sample_match_recommendation.counter_matrix.primary_unit_recommendation
    assert explanation.economic_plan.problem_diagnosis != ""
    assert len(explanation.priority_checklist) >= 2
    assert "Town Center" in explanation.economic_plan.macro_tip or "farm" in explanation.economic_plan.macro_tip.lower()


def test_deterministic_fallback_explainer_advanced(sample_match_recommendation):
    explanation = DeterministicFallbackExplainer.generate_explanation(
        sample_match_recommendation,
        elo_tier_override=ELOTier.ADVANCED,
    )

    assert explanation.elo_tier == ELOTier.ADVANCED
    assert "high ground" in explanation.military_plan.micro_positioning_tip.lower() or "split" in explanation.military_plan.micro_positioning_tip.lower()


def test_tactical_explanation_engine_force_fallback(sample_match_recommendation):
    engine = TacticalExplanationEngine(force_fallback=True)
    res: VerifiedCoachingResponse = engine.explain(sample_match_recommendation)

    assert res.was_fallback_used is True
    assert res.model_used == "deterministic_fallback_v1"
    assert res.verification.is_valid is True
    assert res.explanation.military_plan.primary_unit_recommendation == sample_match_recommendation.counter_matrix.primary_unit_recommendation


@patch("requests.post")
def test_tactical_explanation_engine_with_mocked_llm(mock_post, sample_match_recommendation):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "primary_directive": "CASTLE AGE KNIGHT CRUSH",
                        "coach_summary": "Exploit Franks heavy cavalry advantage against Viking infantry.",
                        "military_plan": {
                            "primary_unit_recommendation": "Knight",
                            "secondary_unit_recommendation": "Monk",
                            "production_building_instruction": "Add 2 Stables for 3 total Stables",
                            "key_tech_priorities": ["Chain Barding Armor", "Husbandry"],
                            "counter_explanation": "Knights cleanly defeat Castle Age infantry.",
                            "micro_positioning_tip": "Patrol into engagements.",
                        },
                        "economic_plan": {
                            "problem_diagnosis": "Floating 750 wood while starving on gold.",
                            "immediate_action": "Move 8 woodcutters to farms and 4 to gold.",
                            "target_villager_allocation": {
                                "food": 22,
                                "wood": 14,
                                "gold": 10,
                                "stone": 2,
                            },
                            "macro_tip": "Keep Town Centers producing villagers non-stop.",
                        },
                        "timing_plan": {
                            "posture": "Aggressive Castle Age Timing",
                            "attack_window": "Next 3-5 minutes",
                            "threat_alert": "Watch for Viking Imperial Berserkergang transition.",
                            "strategic_spike_reasoning": "Franks cavalry HP power spike in Castle Age.",
                        },
                        "priority_checklist": [
                            "1. Drop 2 more Stables",
                            "2. Move 8 woodcutters to farms",
                            "3. Attack within 3-5 minutes",
                        ],
                    })
                }
            }
        ]
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    engine = TacticalExplanationEngine(
        config=LLMConfig(base_url="http://localhost:11434/v1", model="llama3.2")
    )
    res: VerifiedCoachingResponse = engine.explain(sample_match_recommendation)

    assert res.was_fallback_used is False
    assert res.model_used == "llama3.2"
    assert res.verification.is_valid is True
    assert res.explanation.primary_directive == "CASTLE AGE KNIGHT CRUSH"
    assert res.generation_latency_ms >= 0.0


@patch("requests.post")
def test_tactical_explanation_engine_auto_fallback_on_network_error(mock_post, sample_match_recommendation):
    # Simulate connection error to Ollama/llama.cpp
    import requests
    mock_post.side_effect = requests.exceptions.ConnectionError("Failed to connect to localhost:11434")

    engine = TacticalExplanationEngine()
    res: VerifiedCoachingResponse = engine.explain(sample_match_recommendation)

    # Should gracefully succeed using fallback engine without crashing
    assert res.was_fallback_used is True
    assert res.model_used == "deterministic_fallback_v1"
    assert res.explanation.military_plan.primary_unit_recommendation == sample_match_recommendation.counter_matrix.primary_unit_recommendation
    assert res.verification.is_valid is True


@pytest.mark.asyncio
@patch("requests.post")
async def test_tactical_explanation_engine_async(mock_post, sample_match_recommendation):
    mock_resp = MagicMock()
    mock_resp.json.return_value = {
        "choices": [
            {
                "message": {
                    "content": json.dumps({
                        "primary_directive": "ASYNC CAVALRY RUSH",
                        "coach_summary": "Summary",
                        "military_plan": {
                            "primary_unit_recommendation": "Knight",
                            "secondary_unit_recommendation": None,
                            "production_building_instruction": "3 Stables",
                            "key_tech_priorities": ["Chain Barding Armor"],
                            "counter_explanation": "Explanation",
                            "micro_positioning_tip": "Tip",
                        },
                        "economic_plan": {
                            "problem_diagnosis": "Diagnosis",
                            "immediate_action": "Action",
                            "target_villager_allocation": {"food": 20, "wood": 18, "gold": 8, "stone": 2},
                            "macro_tip": "Tip",
                        },
                        "timing_plan": {
                            "posture": "Posture",
                            "attack_window": "Window",
                            "threat_alert": None,
                            "strategic_spike_reasoning": "Reason",
                        },
                        "priority_checklist": ["1. Action"],
                    })
                }
            }
        ]
    }
    mock_resp.raise_for_status.return_value = None
    mock_post.return_value = mock_resp

    engine = TacticalExplanationEngine()
    res: VerifiedCoachingResponse = await engine.async_explain(sample_match_recommendation)
    assert res.was_fallback_used is False
    assert res.explanation.primary_directive == "ASYNC CAVALRY RUSH"
