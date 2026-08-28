#!/usr/bin/env python3
"""
CLI script to harvest match metadata and recorded games.
Usage:
    python scripts/run_harvest.py --count 50
"""

import os
import argparse
import logging
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aoe2_coach.pipeline.harvester import ReplayHarvester, SEED_PRO_PROFILE_IDS

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("run_harvest")


def main():
    parser = argparse.ArgumentParser(description="Harvest AoE2:DE match metadata and replays")
    parser.add_argument("--profiles", nargs="+", type=int, default=None, help="Specific player profile IDs to scrape")
    parser.add_argument("--count-per-profile", type=int, default=20, help="Number of recent matches per profile")
    parser.add_argument("--raw-dir", type=str, default="data/raw", help="Output directory for raw .aoe2record files")
    parser.add_argument("--db-path", type=str, default="data/metadata/matches.db", help="SQLite metadata DB path")
    parser.add_argument("--download", action="store_true", help="Attempt downloading replay files for harvested matches")

    args = parser.parse_args()

    harvester = ReplayHarvester(
        raw_storage_dir=args.raw_dir,
        metadata_db_path=args.db_path,
    )

    profiles = args.profiles or SEED_PRO_PROFILE_IDS[:5]
    logger.info(f"Starting harvest for {len(profiles)} player profiles (count_per_profile={args.count_per_profile})...")

    harvested = harvester.harvest_matches_for_profiles(
        profile_ids=profiles,
        count_per_profile=args.count_per_profile,
    )

    stats = harvester.metadata_store.count_matches()
    logger.info(f"Harvest complete. Database stats: {stats['total_indexed']} total indexed matches.")

    if args.download:
        pending = harvester.metadata_store.get_pending_downloads(limit=10)
        logger.info(f"Attempting download for {len(pending)} pending matches...")
        for mid in pending:
            harvester.download_replay(mid)


if __name__ == "__main__":
    main()
