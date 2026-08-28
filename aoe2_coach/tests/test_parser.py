"""
Tests for ReplayParser.
"""

import os
import pytest
from aoe2_coach.pipeline.parser import (
    ReplayParser,
    ParsedReplayData,
    TrainEvent,
    ResearchEvent,
    BuildEvent,
)

SAMPLE_REC = "/home/djorgs/Downloads/SD-AgeIIDE_Replay_502556700.aoe2record"


def test_parser_file_not_found():
    parser = ReplayParser()
    with pytest.raises(FileNotFoundError):
        parser.parse_file("/non/existent/path.aoe2record")


def test_parser_empty_bytes():
    parser = ReplayParser()
    with pytest.raises(ValueError):
        parser.parse_bytes(b"")


@pytest.mark.skipif(not os.path.exists(SAMPLE_REC), reason="Sample replay file not present in Downloads")
def test_parser_sample_replay():
    parser = ReplayParser()
    parsed = parser.parse_file(SAMPLE_REC)

    assert isinstance(parsed, ParsedReplayData)
    assert parsed.metadata.match_id == "502556700"
    assert parsed.metadata.map_name == "Arabia"
    assert len(parsed.metadata.players) == 2
    assert parsed.metadata.duration_sec > 1000.0

    # Ensure events are sorted
    timestamps = [e.timestamp_sec for e in parsed.events]
    assert timestamps == sorted(timestamps)

    # Check key event types exist
    train_events = [e for e in parsed.events if isinstance(e, TrainEvent)]
    research_events = [e for e in parsed.events if isinstance(e, ResearchEvent)]
    build_events = [e for e in parsed.events if isinstance(e, BuildEvent)]

    assert len(train_events) > 50
    assert len(research_events) > 10
    assert len(build_events) > 50
