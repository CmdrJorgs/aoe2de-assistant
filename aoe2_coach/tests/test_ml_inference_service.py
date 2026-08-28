"""
Integration Tests for MLInferenceService and Latency Guarantees.
"""

import pytest
import numpy as np

from aoe2_coach.models.inference_service import MLInferenceService, MLRecommendation
from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    ResourceStockpile,
    VillagerAllocation,
    SightedEntity,
    TargetLabels,
)


def test_ml_inference_service_recommendation_from_dict():
    service = MLInferenceService()
    state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "player_elo": 1100,
        "timestamp_sec": 1350,
        "food": 350,
        "wood": 750,
        "gold": 120,
        "stone": 200,
        "vills_total": 45,
        "vills_food": 14,
        "vills_wood": 22,
        "vills_gold": 7,
        "vills_stone": 2,
        "military_total": 8,
        "cavalry_count": 6,
        "opp_sighted_infantry": 5,
    }

    rec = service.get_recommendation(state)
    assert isinstance(rec, MLRecommendation)
    assert rec.match_context.player_civ == "Franks"
    assert rec.match_context.opponent_civ == "Vikings"
    assert rec.match_context.player_age == 3
    assert "CASTLE AGE" in rec.primary_directive
    assert 0.0 <= rec.win_probability.win_probability <= 1.0
    assert rec.military_action_plan.primary_composition != ""
    assert rec.economic_rebalance.target_allocation.total == 45
    assert len(rec.actionable_checklist) >= 3
    assert rec.inference_latency_ms >= 0.0


def test_ml_inference_service_recommendation_from_snapshot():
    service = MLInferenceService()
    snapshot = GameSnapshot(
        match_id="match_999",
        patch_version="101.102.x",
        timestamp_sec=1400,
        map_type="Arabia",
        player=PlayerState(
            player_id=1,
            civ_id=1,
            civ_name="Britons",
            elo=1250,
            age=3,
            resources=ResourceStockpile(food=200, wood=500, gold=180, stone=0),
            villagers=VillagerAllocation(total=50, food=16, wood=24, gold=10, stone=0),
            military_units={"crossbowman": 18},
            completed_techs=["bodkin_arrow", "fletching"],
        ),
        opponent_observed=OpponentObservedState(
            civ_id=3,
            civ_name="Goths",
            estimated_age=3,
            sighted_units=[SightedEntity(entity_name="huskarl", entity_type="unit", count=6, last_seen_sec=1350)],
        ),
        label=TargetLabels(winner=True),
    )

    rec = service.get_recommendation(snapshot)
    assert isinstance(rec, MLRecommendation)
    assert rec.match_context.player_civ == "Britons"
    assert rec.match_context.opponent_civ == "Goths"
    assert len(rec.counter_matrix.recommended_counters) > 0


def test_ml_inference_service_latency_sub_20ms():
    service = MLInferenceService()
    bench = service.benchmark_latency(iterations=50)
    assert bench["p99_ms"] < 25.0
    assert bench["sub_20ms_pass"] is True
