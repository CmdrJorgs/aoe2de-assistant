"""
Tests for SnapshotExtractor.
"""

import os
import pytest
from aoe2_coach.pipeline.parser import ReplayParser
from aoe2_coach.pipeline.snapshot_extractor import SnapshotExtractor
from aoe2_coach.schemas.match import GameSnapshot

SAMPLE_REC = "/home/djorgs/Downloads/SD-AgeIIDE_Replay_502556700.aoe2record"


@pytest.mark.skipif(not os.path.exists(SAMPLE_REC), reason="Sample replay not found in Downloads")
def test_snapshot_extractor_on_sample():
    parser = ReplayParser()
    parsed = parser.parse_file(SAMPLE_REC)

    extractor = SnapshotExtractor(interval_sec=120, start_time_sec=360)
    snapshots = extractor.extract_snapshots(parsed)

    assert len(snapshots) > 10
    for s in snapshots:
        assert isinstance(s, GameSnapshot)
        assert s.timestamp_sec >= 360
        assert s.player.civ_name in ["Lithuanians", "Magyars"]
        assert s.player.age in [1, 2, 3, 4]
        assert s.player.resources.food >= 0
        assert s.player.villagers.total >= 3

        flat = s.to_flat_dict()
        assert "player_food" in flat
        assert "label_winner" in flat
        assert "opponent_civ_name" in flat
