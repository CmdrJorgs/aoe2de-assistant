"""
Tests for DatasetExporter and Parquet writing.
"""

import os
import tempfile
import pytest
import duckdb

from aoe2_coach.pipeline.parser import ReplayParser
from aoe2_coach.pipeline.snapshot_extractor import SnapshotExtractor
from aoe2_coach.pipeline.dataset_exporter import DatasetExporter

SAMPLE_REC = "/home/djorgs/Downloads/SD-AgeIIDE_Replay_502556700.aoe2record"


@pytest.mark.slow
@pytest.mark.skipif(not os.path.exists(SAMPLE_REC), reason="Sample replay not found in Downloads")
def test_dataset_exporter_batch_and_duckdb():
    with tempfile.TemporaryDirectory() as tmpdir:
        out_parquet = os.path.join(tmpdir, "test_snapshots.parquet")
        exporter = DatasetExporter(output_dir=tmpdir)

        stats = exporter.process_replay_batch(
            replay_files=[SAMPLE_REC],
            output_parquet_path=out_parquet,
            max_workers=1,
            interval_sec=120,
        )

        assert stats.successful_files == 1
        assert stats.failed_files == 0
        assert stats.total_snapshots > 0
        assert os.path.exists(out_parquet)

        # Validate with DuckDB
        con = duckdb.connect()
        df = con.execute(f"SELECT * FROM '{out_parquet}'").df()
        assert len(df) == stats.total_snapshots
        assert "player_food" in df.columns
        assert "label_winner" in df.columns


def test_dataset_exporter_synthetic_and_partitioning():
    """Fast in-memory unit test for parquet export and patch partitioning."""
    with tempfile.TemporaryDirectory() as tmpdir:
        exporter = DatasetExporter(output_dir=tmpdir)
        records = [
            {
                "match_id": "test_1",
                "patch_version": "101.102.x",
                "timestamp_sec": 600,
                "map_type": "Arabia",
                "player_civ_id": 1,
                "player_civ_name": "Britons",
                "player_elo": 1200,
                "player_age": 2,
                "player_food": 200,
                "player_wood": 150,
                "player_gold": 100,
                "player_stone": 50,
                "player_vills_total": 22,
                "player_vills_food": 10,
                "player_vills_wood": 8,
                "player_vills_gold": 4,
                "player_vills_stone": 0,
                "player_military_total": 4,
                "player_tech_count": 2,
                "opponent_civ_id": 2,
                "opponent_civ_name": "Franks",
                "opponent_estimated_age": 2,
                "opponent_sighted_units_count": 2,
                "opponent_sighted_buildings_count": 1,
                "label_winner": True,
                "label_next_unit": "archer",
                "label_next_tech": "fletching",
                "label_next_building": "archery_range",
                "label_primary_comp": "crossbow_line",
            },
            {
                "match_id": "test_2",
                "patch_version": "101.103.x",
                "timestamp_sec": 900,
                "map_type": "Arabia",
                "player_civ_id": 46,
                "player_civ_name": "Jurchens",
                "player_elo": 1300,
                "player_age": 3,
                "player_food": 400,
                "player_wood": 300,
                "player_gold": 250,
                "player_stone": 100,
                "player_vills_total": 35,
                "player_vills_food": 16,
                "player_vills_wood": 12,
                "player_vills_gold": 7,
                "player_vills_stone": 0,
                "player_military_total": 8,
                "player_tech_count": 5,
                "opponent_civ_id": 1,
                "opponent_civ_name": "Britons",
                "opponent_estimated_age": 3,
                "opponent_sighted_units_count": 6,
                "opponent_sighted_buildings_count": 3,
                "label_winner": True,
                "label_next_unit": "iron_pagoda",
                "label_next_tech": "iron_casting",
                "label_next_building": "castle",
                "label_primary_comp": "knight_line",
            },
        ]

        out_parquet = os.path.join(tmpdir, "all.parquet")
        count = exporter.write_flat_records_to_parquet(records, out_parquet)
        assert count == 2
        assert os.path.exists(out_parquet)

        partitioned = exporter.write_partitioned_by_patch(records)
        assert "101.102.x" in partitioned
        assert "101.103.x" in partitioned
        assert os.path.exists(partitioned["101.102.x"])
        assert os.path.exists(partitioned["101.103.x"])

        # Validate with DuckDB
        con = duckdb.connect()
        df_102 = con.execute(f"SELECT * FROM '{partitioned['101.102.x']}'").df()
        assert len(df_102) == 1
        assert df_102["player_civ_name"].iloc[0] == "Britons"

        df_103 = con.execute(f"SELECT * FROM '{partitioned['101.103.x']}'").df()
        assert len(df_103) == 1
        assert df_103["player_civ_name"].iloc[0] == "Jurchens"
