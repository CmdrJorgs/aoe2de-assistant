"""
Batch Replay Dataset Exporter: Process collections of replays in parallel and export snapshot vectors to Apache Parquet.
"""

import os
import glob
import time
import logging
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Tuple

import pyarrow as pa
import pyarrow.parquet as pq

from aoe2_coach.schemas.match import GameSnapshot
from aoe2_coach.pipeline.parser import ReplayParser
from aoe2_coach.pipeline.snapshot_extractor import SnapshotExtractor

logger = logging.getLogger(__name__)


# Standard PyArrow Schema for Snapshots
SNAPSHOT_PYARROW_SCHEMA = pa.schema([
    ("match_id", pa.string()),
    ("patch_version", pa.string()),
    ("timestamp_sec", pa.int32()),
    ("map_type", pa.string()),
    # Player state features
    ("player_civ_id", pa.int32()),
    ("player_civ_name", pa.string()),
    ("player_elo", pa.int32()),
    ("player_age", pa.int32()),
    ("player_food", pa.int32()),
    ("player_wood", pa.int32()),
    ("player_gold", pa.int32()),
    ("player_stone", pa.int32()),
    ("player_vills_total", pa.int32()),
    ("player_vills_food", pa.int32()),
    ("player_vills_wood", pa.int32()),
    ("player_vills_gold", pa.int32()),
    ("player_vills_stone", pa.int32()),
    ("player_military_total", pa.int32()),
    ("player_tech_count", pa.int32()),
    # Opponent observed features
    ("opponent_civ_id", pa.int32()),
    ("opponent_civ_name", pa.string()),
    ("opponent_estimated_age", pa.int32()),
    ("opponent_sighted_units_count", pa.int32()),
    ("opponent_sighted_buildings_count", pa.int32()),
    # Target outcome labels
    ("label_winner", pa.bool_()),
    ("label_next_unit", pa.string()),
    ("label_next_tech", pa.string()),
    ("label_next_building", pa.string()),
    ("label_primary_comp", pa.string()),
])


def _process_single_replay_file(
    filepath: str, interval_sec: int = 120
) -> Tuple[str, Optional[List[Dict[str, Any]]], Optional[str]]:
    """Worker function for parallel multiprocessing pool."""
    try:
        parser = ReplayParser()
        parsed_data = parser.parse_file(filepath)
        extractor = SnapshotExtractor(interval_sec=interval_sec)
        snapshots = extractor.extract_snapshots(parsed_data)
        flat_records = [s.to_flat_dict() for s in snapshots]
        return (filepath, flat_records, None)
    except Exception as e:
        return (filepath, None, str(e))


@dataclass
class PipelineStats:
    total_files: int = 0
    successful_files: int = 0
    failed_files: int = 0
    total_snapshots: int = 0
    elapsed_sec: float = 0.0
    throughput_snapshots_per_sec: float = 0.0


class DatasetExporter:
    """Exports snapshots to Parquet format and manages batch pipelines."""

    def __init__(self, output_dir: str = "data/processed"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def write_snapshots_to_parquet(
        self, snapshots: List[GameSnapshot], output_filepath: str
    ) -> int:
        """Write a list of GameSnapshot instances directly to a Parquet file."""
        if not snapshots:
            logger.warning("No snapshots to write to Parquet.")
            return 0

        flat_dicts = [s.to_flat_dict() for s in snapshots]
        return self.write_flat_records_to_parquet(flat_dicts, output_filepath)

    def write_flat_records_to_parquet(
        self, records: List[Dict[str, Any]], output_filepath: str
    ) -> int:
        """Write pre-flattened snapshot dictionary records to a Parquet file."""
        if not records:
            return 0

        # Build columnar arrays for PyArrow Table
        table = pa.Table.from_pylist(records, schema=SNAPSHOT_PYARROW_SCHEMA)
        os.makedirs(os.path.dirname(os.path.abspath(output_filepath)), exist_ok=True)
        pq.write_table(table, output_filepath, compression="snappy")
        return len(records)

    def process_replay_batch(
        self,
        replay_files: List[str],
        output_parquet_path: str,
        max_workers: int = 4,
        interval_sec: int = 120,
    ) -> PipelineStats:
        """Process a collection of replay files in parallel and save combined Parquet dataset."""
        start_time = time.time()
        all_records: List[Dict[str, Any]] = []
        successful_count = 0
        failed_count = 0

        logger.info(f"Starting batch processing of {len(replay_files)} replays with {max_workers} workers...")

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_file = {
                executor.submit(_process_single_replay_file, f, interval_sec): f
                for f in replay_files
            }

            for future in as_completed(future_to_file):
                filepath = future_to_file[future]
                try:
                    fpath, records, error = future.result()
                    if error:
                        failed_count += 1
                        logger.error(f"Error parsing {filepath}: {error}")
                    else:
                        successful_count += 1
                        if records:
                            all_records.extend(records)
                except Exception as exc:
                    failed_count += 1
                    logger.error(f"Worker exception processing {filepath}: {exc}")

        # Write all records to target Parquet file
        total_snapshots = len(all_records)
        if all_records:
            self.write_flat_records_to_parquet(all_records, output_parquet_path)

        elapsed = max(0.001, time.time() - start_time)
        stats = PipelineStats(
            total_files=len(replay_files),
            successful_files=successful_count,
            failed_files=failed_count,
            total_snapshots=total_snapshots,
            elapsed_sec=round(elapsed, 2),
            throughput_snapshots_per_sec=round(total_snapshots / elapsed, 1),
        )

        logger.info(
            f"Batch completed in {stats.elapsed_sec}s: {stats.successful_files}/{stats.total_files} files parsed successfully. "
            f"Extracted {stats.total_snapshots} snapshots ({stats.throughput_snapshots_per_sec} snapshots/sec)."
        )
        return stats
