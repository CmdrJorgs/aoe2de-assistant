"""
Tests for ReplayHarvester and MetadataStore.
"""

import os
import tempfile
import pytest
from aoe2_coach.pipeline.harvester import (
    MetadataStore,
    HarvestedMatch,
    ReplayHarvester,
)


def test_metadata_store_upsert_and_query():
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = os.path.join(tmpdir, "matches.db")
        store = MetadataStore(db_path=db_path)

        match1 = HarvestedMatch(
            match_id=101,
            started="2026-08-28T12:00:00Z",
            map_name="Arabia",
            leaderboard="1v1 RM",
            player1_name="PlayerA",
            player1_elo=1500,
            player1_civ="Franks",
            player2_name="PlayerB",
            player2_elo=1520,
            player2_civ="Vikings",
            winner_name="PlayerA",
            file_id="sample_file_id_abc123",
            downloaded=False,
        )

        store.upsert_match(match1)
        counts = store.count_matches()
        assert counts["total_indexed"] == 1
        assert counts["total_downloaded"] == 0

        pending_ids = store.get_pending_downloads(limit=10)
        assert pending_ids == [101]

        pending_matches = store.get_pending_matches(limit=10)
        assert len(pending_matches) == 1
        assert pending_matches[0].match_id == 101
        assert pending_matches[0].file_id == "sample_file_id_abc123"

        # Update to downloaded via mark_downloaded
        store.mark_downloaded(101, "/path/to/101.aoe2record")

        counts2 = store.count_matches()
        assert counts2["total_indexed"] == 1
        assert counts2["total_downloaded"] == 1
        assert len(store.get_pending_matches()) == 0
