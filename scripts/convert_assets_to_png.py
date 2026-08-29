#!/usr/bin/env python3
"""
Convert DDS Assets in buildings/ and tech/ (or any specified directory) to PNG format.

This script scans target directories under `frontend/public/aoe2_assets/`,
opens each DDS file with Pillow, converts it to RGBA PNG format, and removes
the original DDS file.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Tuple

from PIL import Image

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("asset_converter")


def convert_directory_dds_to_png(
    target_dir: Path,
    dry_run: bool = False,
    keep_dds: bool = False,
) -> Tuple[int, int]:
    """
    Convert all DDS images in target_dir to PNG format.

    Returns:
        Tuple of (converted_count, errors_count)
    """
    if not target_dir.exists():
        logger.error("Directory does not exist: %s", target_dir)
        return 0, 1

    files = sorted(os.listdir(target_dir))
    dds_files = [f for f in files if f.lower().endswith(".dds")]
    logger.info("Found %d DDS files in %s", len(dds_files), target_dir)

    converted_count = 0
    errors_count = 0

    for filename in dds_files:
        src_path = target_dir / filename
        stem = Path(filename).stem
        dst_filename = f"{stem}.png"
        dst_path = target_dir / dst_filename

        if dry_run:
            logger.info("[DRY RUN] %s -> %s", filename, dst_filename)
            converted_count += 1
            continue

        try:
            with Image.open(src_path) as img:
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img.save(dst_path, format="PNG")

            converted_count += 1

            if not keep_dds:
                src_path.unlink()

        except Exception as e:
            logger.error("Error processing %s: %s", filename, e)
            errors_count += 1

    return converted_count, errors_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert DDS images in specified asset directories to PNG."
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        default=[
            "frontend/public/aoe2_assets/buildings",
            "frontend/public/aoe2_assets/tech",
        ],
        help="Directories to process (default: buildings and tech)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate conversions without making changes",
    )
    parser.add_argument(
        "--keep-dds",
        action="store_true",
        help="Keep original DDS files after converting to PNG",
    )

    args = parser.parse_args()

    total_converted = 0
    total_errors = 0

    for d in args.dirs:
        dir_path = Path(d).resolve()
        logger.info("Processing directory: %s", dir_path)
        converted, errors = convert_directory_dds_to_png(
            target_dir=dir_path,
            dry_run=args.dry_run,
            keep_dds=args.keep_dds,
        )
        total_converted += converted
        total_errors += errors
        logger.info(
            "Finished %s - Converted: %d, Errors: %d",
            dir_path.name,
            converted,
            errors,
        )

    logger.info(
        "All directories complete! Total Converted: %d, Total Errors: %d",
        total_converted,
        total_errors,
    )

    if total_errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
