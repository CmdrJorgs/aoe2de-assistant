"""
Tests for PlayerStateTracker and GameStateSimulator.
"""

import pytest
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.schemas.match import PlayerMetadata, MatchMetadata
from aoe2_coach.pipeline.parser import (
    ParsedReplayData,
    TrainEvent,
    ResearchEvent,
    BuildEvent,
)
from aoe2_coach.pipeline.simulator import PlayerStateTracker, GameStateSimulator


def test_player_state_tracker_init():
    meta = PlayerMetadata(
        player_id=1,
        name="TestFranks",
        civ_id=2,
        civ_name="Franks",
        elo=1400,
        winner=True,
    )
    tracker = PlayerStateTracker(meta)

    assert tracker.age == Age.DARK
    assert tracker.vills_food == 3
    assert tracker.military_units.get("scout_cavalry") == 1
    assert tracker.resources["food"] == 200
    assert tracker.resources["wood"] == 200


def test_player_state_tracker_events_and_gather():
    meta = PlayerMetadata(
        player_id=1,
        name="TestFranks",
        civ_id=2,
        civ_name="Franks",
        elo=1400,
        winner=True,
    )
    tracker = PlayerStateTracker(meta)

    # Train a villager at t=10s
    tracker.apply_event(TrainEvent(timestamp_sec=10.0, player_id=1, unit_id=83, canonical_name="villager", amount=1, building_type=109))
    assert tracker.vills_food == 4

    # Build a stable at t=120s
    tracker.apply_event(BuildEvent(timestamp_sec=120.0, player_id=1, building_id=101, canonical_name="stable", x=50.0, y=50.0))
    assert tracker.buildings.get("stable") == 1

    # Research Feudal Age at t=200s
    tracker.apply_event(ResearchEvent(timestamp_sec=200.0, player_id=1, tech_id=101, canonical_name="feudal_age", building_id=109))
    assert tracker.age == Age.FEUDAL
    assert "feudal_age" in tracker.completed_techs

    # Export state at t=300s
    state = tracker.to_player_state()
    assert state.age == 2
    assert state.age_name == "Feudal Age"
    assert state.villagers.total >= 4
    assert state.resources.food > 0
    assert state.resources.wood > 0


def test_simulator_step_to_time():
    p1 = PlayerMetadata(player_id=1, name="P1", civ_id=2, civ_name="Franks", elo=1300, winner=True)
    p2 = PlayerMetadata(player_id=2, name="P2", civ_id=11, civ_name="Vikings", elo=1250, winner=False)
    meta = MatchMetadata(
        match_id="m1",
        patch_version="DE_1",
        duration_sec=600.0,
        players=[p1, p2],
        winning_player_id=1,
    )
    events = [
        TrainEvent(timestamp_sec=25.0, player_id=1, unit_id=83, canonical_name="villager", amount=1, building_type=109),
        TrainEvent(timestamp_sec=25.0, player_id=2, unit_id=83, canonical_name="villager", amount=1, building_type=109),
        ResearchEvent(timestamp_sec=300.0, player_id=1, tech_id=101, canonical_name="feudal_age", building_id=109),
    ]
    parsed_data = ParsedReplayData(metadata=meta, events=events)
    sim = GameStateSimulator(parsed_data)

    states_100s = sim.step_to_time(100.0)
    assert states_100s[1].age == Age.DARK
    assert states_100s[1].villagers.total == 4

    states_350s = sim.step_to_time(350.0)
    assert states_350s[1].age == Age.FEUDAL
    assert states_350s[2].age == Age.DARK
