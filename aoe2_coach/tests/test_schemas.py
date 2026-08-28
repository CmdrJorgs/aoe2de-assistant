"""
Tests for schemas and game constants.
"""

import pytest
from aoe2_coach.schemas.game_constants import (
    Age,
    get_civ_name,
    get_canonical_object_name,
    get_canonical_tech_name,
    CIVILIZATIONS,
    CIV_NAME_TO_ID,
)
from aoe2_coach.schemas.match import (
    ResourceStockpile,
    VillagerAllocation,
    PlayerMetadata,
    MatchMetadata,
    PlayerState,
    SightedEntity,
    OpponentObservedState,
    TargetLabels,
    GameSnapshot,
)


def test_age_enum():
    assert Age.DARK == 1
    assert Age.FEUDAL == 2
    assert Age.CASTLE == 3
    assert Age.IMPERIAL == 4
    assert Age.from_name("Castle Age") == Age.CASTLE
    assert Age.from_name("feudal") == Age.FEUDAL
    assert Age.from_name("imp") == Age.IMPERIAL
    assert Age.FEUDAL.display_name == "Feudal Age"


def test_constants_resolution():
    assert get_civ_name(2) == "Franks"
    assert get_civ_name(11) == "Vikings"
    assert get_civ_name(35) == "Lithuanians"
    assert get_civ_name(22) == "Magyars"
    assert get_civ_name(999) == "Unknown Civ (999)"

    assert get_canonical_object_name(83) == "villager"
    assert get_canonical_object_name(38) == "knight"
    assert get_canonical_object_name(109) == "town_center"
    assert get_canonical_object_name(101) == "stable"
    assert get_canonical_object_name(50) == "farm"

    assert get_canonical_tech_name(22) == "loom"
    assert get_canonical_tech_name(101) == "feudal_age"
    assert get_canonical_tech_name(102) == "castle_age"
    assert get_canonical_tech_name(435) == "bloodlines"


def test_player_and_snapshot_serialization():
    player = PlayerState(
        player_id=1,
        civ_id=2,
        civ_name="Franks",
        elo=1200,
        age=3,
        age_name="Castle Age",
        resources=ResourceStockpile(food=350, wood=200, gold=150, stone=100),
        villagers=VillagerAllocation(total=40, food=20, wood=14, gold=6, stone=0),
        military_units={"knight": 4},
        buildings={"town_center": 2, "stable": 2},
        completed_techs=["bloodlines", "scale_barding_armor"],
    )

    observed = OpponentObservedState(
        civ_id=11,
        civ_name="Vikings",
        estimated_age=3,
        estimated_age_name="Castle Age",
        sighted_units=[
            SightedEntity(entity_name="berserk", entity_type="unit", count=5, last_seen_sec=900.0, confidence=0.85)
        ],
        sighted_buildings=[
            SightedEntity(entity_name="castle", entity_type="building", count=1, last_seen_sec=800.0, confidence=1.0)
        ],
    )

    labels = TargetLabels(
        winner=True,
        next_unit_produced="knight",
        next_tech_researched="chain_barding_armor",
        next_building_built="stable",
        primary_composition_next_5m="knight",
    )

    snapshot = GameSnapshot(
        match_id="test_12345",
        patch_version="DE_101.102",
        timestamp_sec=960,
        map_type="Arabia",
        player=player,
        opponent_observed=observed,
        label=labels,
    )

    flat = snapshot.to_flat_dict()
    assert flat["match_id"] == "test_12345"
    assert flat["player_civ_name"] == "Franks"
    assert flat["player_age"] == 3
    assert flat["player_food"] == 350
    assert flat["player_wood"] == 200
    assert flat["player_vills_total"] == 40
    assert flat["label_winner"] is True
    assert flat["label_next_unit"] == "knight"
    assert flat["opponent_civ_name"] == "Vikings"
    assert flat["opponent_sighted_units_count"] == 5
