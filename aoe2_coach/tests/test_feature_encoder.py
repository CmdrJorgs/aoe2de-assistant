"""
Unit Tests for Feature Encoder & State Vectorizer.
"""

import pytest
import numpy as np
import pandas as pd

from aoe2_coach.models.feature_encoder import (
    FeatureEncoder,
    FEATURE_NAMES,
    CIV_ARCHETYPES,
    UNIT_CATEGORY_MAP,
)
from aoe2_coach.schemas.match import (
    GameSnapshot,
    PlayerState,
    OpponentObservedState,
    ResourceStockpile,
    VillagerAllocation,
    SightedEntity,
    TargetLabels,
)


def test_feature_encoder_dimensions_and_names():
    encoder = FeatureEncoder()
    assert len(encoder.feature_names) == 65
    assert encoder.num_features == 65
    assert "timestamp_min" in encoder.feature_names
    assert "rel_military_advantage" in encoder.feature_names


def test_encode_dict_basic():
    encoder = FeatureEncoder()
    state = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_age": 3,
        "player_elo": 1100,
        "timestamp_sec": 1200,
        "food": 400,
        "wood": 300,
        "gold": 200,
        "stone": 100,
        "vills_total": 40,
        "vills_food": 16,
        "vills_wood": 14,
        "vills_gold": 8,
        "vills_stone": 2,
        "military_total": 10,
        "cavalry_count": 8,
        "archer_count": 2,
    }
    vec = encoder.encode_dict(state)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (65,)
    assert vec.dtype == np.float32
    assert not np.isnan(vec).any()


def test_encode_snapshot():
    encoder = FeatureEncoder()
    snapshot = GameSnapshot(
        match_id="test_001",
        patch_version="101.102.x",
        timestamp_sec=1200,
        map_type="Arabia",
        player=PlayerState(
            player_id=1,
            civ_id=2,
            civ_name="Franks",
            elo=1150,
            age=3,
            resources=ResourceStockpile(food=400, wood=350, gold=150, stone=0),
            villagers=VillagerAllocation(total=42, food=18, wood=16, gold=8, stone=0),
            military_units={"knight": 6, "scout_cavalry": 2},
            completed_techs=["bloodlines", "scale_barding_armor"],
        ),
        opponent_observed=OpponentObservedState(
            civ_id=11,
            civ_name="Vikings",
            estimated_age=3,
            sighted_units=[SightedEntity(entity_name="berserk", entity_type="unit", count=4, last_seen_sec=1100)],
            sighted_buildings=[SightedEntity(entity_name="barracks", entity_type="building", count=2, last_seen_sec=1100)],
        ),
        label=TargetLabels(winner=True, primary_composition_next_5m="knight_line"),
    )

    vec = encoder.encode_snapshot(snapshot)
    assert vec.shape == (65,)
    assert not np.isnan(vec).any()
    # Check player cavalry affinity for Franks
    assert vec[50] == 1.0  # player_cav_affinity for Franks


def test_encode_batch_and_dataframe():
    encoder = FeatureEncoder()
    df = pd.DataFrame([
        {"player_civ": "Britons", "opponent_civ": "Franks", "player_age": 2, "vills_total": 25, "food": 200, "wood": 200, "gold": 100, "stone": 0},
        {"player_civ": "Mongols", "opponent_civ": "Goths", "player_age": 3, "vills_total": 45, "food": 500, "wood": 400, "gold": 250, "stone": 0},
    ])
    X = encoder.encode_dataframe(df)
    assert X.shape == (2, 65)
    assert X.dtype == np.float32
