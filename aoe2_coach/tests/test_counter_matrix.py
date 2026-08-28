"""
Tests for AoE2 Dynamic Counter Matrix Engine & Composition Evaluator.
"""

import pytest
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.rules.counter_matrix import CounterMatrixEngine


def test_threat_analysis_infantry():
    engine = CounterMatrixEngine()
    threat = engine.analyze_threat(
        enemy_units={"berserk": 5},
        enemy_civ="vikings",
        enemy_age=Age.CASTLE,
    )
    assert threat.primary_threat_archetype == "heavy_infantry"
    assert threat.dominant_enemy_unit == "berserk"
    assert "infantry" in threat.detected_armor_classes
    assert threat.total_enemy_count == 5


def test_threat_analysis_cavalry():
    engine = CounterMatrixEngine()
    threat = engine.analyze_threat(
        enemy_units={"knight": 6, "scout_cavalry": 2},
        enemy_civ="franks",
        enemy_age=Age.CASTLE,
    )
    assert threat.primary_threat_archetype == "heavy_cavalry"
    assert threat.dominant_enemy_unit == "knight"
    assert "cavalry" in threat.detected_armor_classes
    assert "Franks" in threat.tactical_warning


def test_franks_counter_vs_vikings_berserkers():
    engine = CounterMatrixEngine()
    result = engine.recommend_counters(
        player_civ="franks",
        player_age=Age.CASTLE,
        enemy_units={"berserk": 5},
        enemy_civ="vikings",
    )
    assert len(result.recommended_counters) > 0
    top_units = [c.unit_name for c in result.recommended_counters]
    # Knights or Throwing Axeman or Crossbows should be recommended counters vs infantry
    assert any(u in top_units for u in ["Knight", "Throwing Axeman", "Crossbowman", "Scorpion"])
    assert result.production_building_target in ["stable", "castle", "archery_range"]


def test_aztecs_counter_vs_mass_knights():
    engine = CounterMatrixEngine()
    result = engine.recommend_counters(
        player_civ="aztecs",
        player_age=Age.CASTLE,
        enemy_units={"knight": 8},
        enemy_civ="franks",
    )
    assert len(result.recommended_counters) > 0
    top_units = [c.unit_name for c in result.recommended_counters]
    # Aztecs cannot make knights; they should recommend Pikeman, Monk, or Jaguar Warrior
    assert "Knight" not in top_units
    assert any(u in top_units for u in ["Pikeman", "Monk", "Jaguar Warrior", "Eagle Warrior"])


def test_britons_counter_vs_mass_crossbows():
    engine = CounterMatrixEngine()
    result = engine.recommend_counters(
        player_civ="britons",
        player_age=Age.CASTLE,
        enemy_units={"crossbowman": 12},
        enemy_civ="ethiopians",
    )
    assert len(result.recommended_counters) > 0
    top_units = [c.unit_name for c in result.recommended_counters]
    # Anti-archer counters: Skirmishers, Mangonels, Longbowmen, Knights
    assert any(u in top_units for u in ["Elite Skirmisher", "Mangonel", "Longbowman", "Knight"])
