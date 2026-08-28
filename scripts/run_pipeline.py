#!/usr/bin/env python3
"""
CLI script to execute the complete Phase 1 Replay Processing & Parquet Export Pipeline.
Usage:
    python scripts/run_pipeline.py --input-dir /path/to/replays --output data/processed/snapshots.parquet
"""

import os
import glob
import argparse
import logging
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aoe2_coach.pipeline.dataset_exporter import DatasetExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_pipeline")


def main():
    parser = argparse.ArgumentParser(description="Process AoE2 recorded games into ML snapshots in Parquet format")
    parser.add_argument("--input-dir", type=str, default="data/raw", help="Directory containing .aoe2record files")
    parser.add_argument("--input-file", type=str, default=None, help="Single .aoe2record file to process")
    parser.add_argument("--output", type=str, default="data/processed/snapshots.parquet", help="Output Parquet path")
    parser.add_argument("--workers", type=int, default=4, help="Number of parallel worker processes")
    parser.add_argument("--interval", type=int, default=120, help="Snapshot interval in seconds (default: 120s / 2min)")

    args = parser.parse_args()

    files = []
    if args.input_file:
        files = [args.input_file]
    else:
        # Search both input-dir and /home/djorgs/Downloads for .aoe2record files
        files.extend(glob.glob(os.path.join(args.input_dir, "*.aoe2record")))
        if not files:
            # Check Downloads folder
            downloads_files = glob.glob("/home/djorgs/Downloads/*.aoe2record")
            if downloads_files:
                logger.info(f"Found {len(downloads_files)} replay(s) in /home/djorgs/Downloads")
                files.extend(downloads_files)

    if not files:
        logger.error(f"No .aoe2record files found in {args.input_dir} or ~/Downloads.")
        sys.exit(1)

    logger.info(f"Found {len(files)} replay file(s) to process.")

    exporter = DatasetExporter()
    stats = exporter.process_replay_batch(
        replay_files=files,
        output_parquet_path=args.output,
        max_workers=args.workers,
        interval_sec=args.interval,
    )

    logger.info(f"Pipeline finished: {stats.total_snapshots} snapshots extracted into {args.output}")


if __name__ == "__main__":
    main()
