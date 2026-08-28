#!/usr/bin/env python3
"""
CLI script to harvest matches and download recorded games from aoe2recs.com archive into local raw storage.
"""

import os
import sys
import argparse
import logging
import time

from aoe2_coach.pipeline.harvester import ReplayHarvester, MetadataStore

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("aoe2_harvester")


def main():
    parser = argparse.ArgumentParser(
        description="AoE2 Replay Harvester - Download recorded games from aoe2recs.com archive."
    )
    parser.add_argument(
        "--raw-dir",
        type=str,
        default="data/raw",
        help="Directory to save raw .aoe2record files (default: data/raw)",
    )
    parser.add_argument(
        "--db-path",
        type=str,
        default="data/metadata/matches.db",
        help="Path to SQLite metadata index database (default: data/metadata/matches.db)",
    )
    parser.add_argument(
        "--max-pages",
        type=int,
        default=None,
        help="Maximum pages to scrape from archive (default: None, scrapes all available)",
    )
    parser.add_argument(
        "--page-size",
        type=int,
        default=50,
        help="Matches per page request (default: 50)",
    )
    parser.add_argument(
        "--download-workers",
        type=int,
        default=6,
        help="Concurrent download worker threads (default: 6)",
    )
    parser.add_argument(
        "--max-downloads",
        type=int,
        default=None,
        help="Maximum replays to download in this run (default: None, downloads all pending)",
    )
    parser.add_argument(
        "--skip-metadata",
        action="store_true",
        help="Skip scraping metadata index and proceed directly to downloading pending replays",
    )
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Only index metadata without downloading .aoe2record files",
    )
    args = parser.parse_args()

    harvester = ReplayHarvester(
        raw_storage_dir=args.raw_dir,
        metadata_db_path=args.db_path,
    )

    # 1. Harvest match metadata from aoe2recs.com archive
    if not args.skip_metadata:
        logger.info("=" * 60)
        logger.info("PHASE 1: Scraping aoe2recs.com 7-day match archive metadata...")
        logger.info("=" * 60)
        t0 = time.time()
        matches = harvester.harvest_aoe2recs_archive(
            max_pages=args.max_pages,
            page_size=args.page_size,
        )
        elapsed = time.time() - t0
        logger.info(f"Indexed {len(matches)} matches in {elapsed:.1f}s.")

    counts = harvester.metadata_store.count_matches()
    logger.info(f"Metadata Store Status: {counts['total_indexed']} total matches indexed, {counts['total_downloaded']} downloaded.")

    # 2. Download pending replays
    if not args.skip_download:
        pending_matches = harvester.metadata_store.get_pending_matches(
            limit=args.max_downloads or 100000
        )
        logger.info("=" * 60)
        logger.info(f"PHASE 2: Downloading {len(pending_matches)} pending .aoe2record replay files...")
        logger.info(f"Target Directory: {os.path.abspath(args.raw_dir)}")
        logger.info("=" * 60)

        t0 = time.time()
        downloaded = 0
        batch_size = 100

        while True:
            limit = min(batch_size, (args.max_downloads - downloaded) if args.max_downloads else batch_size)
            if limit <= 0:
                break

            batch_pending = harvester.metadata_store.get_pending_matches(limit=limit)
            if not batch_pending:
                logger.info("All pending matches processed.")
                break

            batch_count = harvester.download_pending_replays(
                batch_size=limit,
                max_downloads=limit,
                max_workers=args.download_workers,
            )
            downloaded += batch_count
            logger.info(f"Progress: {downloaded} replays downloaded so far...")

            if args.max_downloads and downloaded >= args.max_downloads:
                break

        elapsed = time.time() - t0
        final_counts = harvester.metadata_store.count_matches()
        logger.info("=" * 60)
        logger.info(f"Harvest Summary: Downloaded {downloaded} replay files in {elapsed:.1f}s.")
        logger.info(f"Total Archive: {final_counts['total_downloaded']} downloaded, {final_counts.get('total_failed', 0)} unavailable / {final_counts['total_indexed']} total indexed.")
        logger.info("=" * 60)


if __name__ == "__main__":
    main()
