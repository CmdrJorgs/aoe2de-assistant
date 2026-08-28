"""
Tests for VoiceTranscriptParser.
"""

import pytest
from aoe2_coach.api.voice_parser import VoiceTranscriptParser, parse_number_expression
from aoe2_coach.api.schemas import SnapshotInput


def test_parse_number_expression():
    assert parse_number_expression("5") == 5
    assert parse_number_expression("five") == 5
    assert parse_number_expression("twenty") == 20
    assert parse_number_expression("zero") == 0


def test_voice_parser_full_matchup():
    transcript = "I'm playing Franks vs Vikings at 22 minutes Castle Age. I have 48 villagers with 14 on food, 26 on wood, 6 on gold, 2 on stone. My resources are 320 food, 750 wood, 120 gold, 450 stone. I spotted 5 Berserkers and a Castle."
    
    resp = VoiceTranscriptParser.parse(transcript)
    snap = resp.parsed_snapshot
    
    assert snap.player_civ == "Franks"
    assert snap.opponent_civ == "Vikings"
    assert snap.current_age == 3
    assert snap.game_time_minutes == 22.0
    assert snap.food == 320
    assert snap.wood == 750
    assert snap.gold == 120
    assert snap.stone == 450
    assert snap.vills_total == 48
    assert snap.vills_food == 14
    assert snap.vills_wood == 26
    assert snap.vills_gold == 6
    assert snap.vills_stone == 2
    assert "Berserk" in snap.sighted_enemy_units
    assert snap.sighted_enemy_units["Berserk"] >= 5
    assert "Castle" in snap.sighted_enemy_buildings
    assert snap.sighted_enemy_buildings["Castle"] >= 1
    assert resp.confidence_score > 0.5


def test_voice_parser_elo_and_partial_update():
    current = SnapshotInput(
        player_civ="Britons",
        opponent_civ="Mayans",
        player_elo=1000,
    )
    transcript = "My ELO is 1250 and I just saw 10 crossbows and 2 ranges"
    resp = VoiceTranscriptParser.parse(transcript, current_snapshot=current)
    snap = resp.parsed_snapshot
    
    assert snap.player_elo == 1250
    assert snap.player_civ == "Britons"  # Preserved from existing
    assert snap.opponent_civ == "Mayans"  # Preserved from existing
    assert "Crossbowman" in snap.sighted_enemy_units
    assert snap.sighted_enemy_units["Crossbowman"] == 10
    assert "Archery Range" in snap.sighted_enemy_buildings
    assert snap.sighted_enemy_buildings["Archery Range"] == 2
