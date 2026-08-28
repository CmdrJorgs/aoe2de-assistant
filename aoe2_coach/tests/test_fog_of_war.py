"""
Tests for Fog-of-War and LOS Simulator.
"""

import pytest
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.schemas.match import PlayerMetadata, MatchMetadata
from aoe2_coach.pipeline.parser import (
    ParsedReplayData,
    BuildEvent,
    MoveEvent,
    InteractEvent,
)
from aoe2_coach.pipeline.fog_of_war import PlayerFogOfWarTracker, FogOfWarEngine


def test_player_fow_tracker_sight_and_decay():
    opp_meta = PlayerMetadata(player_id=2, name="Opponent", civ_id=11, civ_name="Vikings")
    tracker = PlayerFogOfWarTracker(player_id=1, opponent_metadata=opp_meta, decay_half_life_sec=120.0)

    # Sight 5 berserks at t=100s
    tracker.sight_enemy_entity("berserk", "unit", x=50.0, y=50.0, timestamp_sec=100.0, count=5)
    # Sight a castle at t=120s
    tracker.sight_enemy_entity("castle", "building", x=52.0, y=52.0, timestamp_sec=120.0, count=1)

    # At t=100s, confidence should be 1.0
    state_100s = tracker.get_observed_state(100.0)
    assert state_100s.civ_name == "Vikings"
    assert len(state_100s.sighted_units) == 1
    assert state_100s.sighted_units[0].confidence == 1.0
    assert state_100s.sighted_units[0].count == 5

    # Castle sight infers Castle Age
    assert state_100s.estimated_age >= Age.CASTLE

    # At t=220s (120s later, exactly 1 half-life), unit confidence should be ~0.5
    state_220s = tracker.get_observed_state(220.0)
    assert abs(state_220s.sighted_units[0].confidence - 0.5) < 0.05
    # Building confidence should remain 1.0
    assert state_220s.sighted_buildings[0].confidence == 1.0


def test_fow_engine_los_discovery():
    p1 = PlayerMetadata(player_id=1, name="P1", civ_id=2, civ_name="Franks")
    p2 = PlayerMetadata(player_id=2, name="P2", civ_id=11, civ_name="Vikings")
    meta = MatchMetadata(
        match_id="m_fow",
        patch_version="DE_1",
        duration_sec=600.0,
        players=[p1, p2],
    )

    # Player 1 builds Town Center at (50, 50) and Player 2 builds Stable at (52, 50) within LOS
    events = [
        BuildEvent(timestamp_sec=10.0, player_id=1, building_id=109, canonical_name="town_center", x=50.0, y=50.0),
        BuildEvent(timestamp_sec=30.0, player_id=2, building_id=101, canonical_name="stable", x=52.0, y=50.0),
    ]

    parsed = ParsedReplayData(metadata=meta, events=events)
    engine = FogOfWarEngine(parsed)

    obs = engine.step_to_time(50.0)
    # Player 1 should have sighted Player 2's stable
    assert any(b.entity_name == "stable" for b in obs[1].sighted_buildings)
