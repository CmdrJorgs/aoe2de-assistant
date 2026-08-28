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
