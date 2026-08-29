#!/usr/bin/env python3
"""
Rename unit images using metadata from CivTechTrees JSON files.

This script parses all JSON files in `frontend/public/aoe2_assets/CivTechTrees/*.json`.
For each entry where "Use Type" is "Unit", "Picture Index" is mapped to the unit image ID.
The script renames `frontend/public/aoe2_assets/units/<ID>_*.png` to `<ID>_<snakecase_name>.png`.
"""

import argparse
import glob
import json
import logging
import os
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Set, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("civ_tech_tree_renamer")


def to_snake_case(text: str) -> str:
    """Convert raw unit label to clean snake_case string."""
    # Normalize accents (e.g. Alençon -> Alencon)
    s = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    # Replace parentheses, slashes, question marks with spaces
    s = re.sub(r"[\(\)\?\/]+", " ", s)
    # Remove apostrophes and quotes
    s = re.sub(r"['\"’]+", "", s)
    # Replace non-alphanumeric characters with underscore
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    s = s.strip("_").lower()
    return s


def parse_civ_tech_trees(tech_trees_dir: Path) -> Dict[int, str]:
    """
    Parse all JSON files in tech_trees_dir and construct a Picture Index -> Unit Name map.
    """
    json_pattern = str(tech_trees_dir / "*.json")
    json_files = glob.glob(json_pattern)
    logger.info("Found %d CivTechTree JSON files in %s", len(json_files), tech_trees_dir)

    pic_map: Dict[int, List[Tuple[str, str]]] = {}

    for jf in json_files:
        civ_name = Path(jf).stem
        try:
            with open(jf, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            logger.warning("Failed to parse %s: %s", jf, e)
            continue

        for key, items in data.items():
            if isinstance(items, list):
                for entry in items:
                    if isinstance(entry, dict):
                        if entry.get("Use Type") == "Unit":
                            pic_idx = entry.get("Picture Index")
                            name = entry.get("Name")
                            if pic_idx is not None and name:
                                pic_map.setdefault(pic_idx, []).append((civ_name, name.strip()))

    unit_name_map: Dict[int, str] = {}
    for pic_idx, entries in sorted(pic_map.items()):
        # Deduplicate while preserving order
        names = list(dict.fromkeys(e[1] for e in entries))
        if len(names) == 1:
            chosen = names[0]
        else:
            # If elite vs non-elite share the index, prefer base name
            non_elites = [n for n in names if not n.lower().startswith("elite ")]
            if non_elites:
                # For Return of Rome IDs >= 600, prefer RoR specific names over AoE2 base names
                ror_names = [
                    n
                    for n in non_elites
                    if n
                    not in [
                        "Militia",
                        "Man-at-Arms",
                        "Long Swordsman",
                        "Champion",
                        "Pikeman",
                        "Halberdier",
                        "Knight",
                        "Hussar",
                        "Cavalier",
                        "Paladin",
                        "Archer",
                        "Crossbowman",
                        "Arbalester",
                        "Hand Cannoneer",
                    ]
                ]
                if ror_names and pic_idx >= 600:
                    chosen = ror_names[0]
                else:
                    chosen = non_elites[0]
            else:
                chosen = names[0]

        unit_name_map[pic_idx] = chosen

    logger.info("Successfully extracted %d unique unit Picture Indexes", len(unit_name_map))
    return unit_name_map


def rename_unit_images(
    units_dir: Path,
    unit_name_map: Dict[int, str],
    dry_run: bool = False,
) -> Tuple[int, int, int]:
    """
    Rename PNG images in units_dir based on unit_name_map.

    Returns:
        Tuple of (renamed_count, already_correct_count, errors_count)
    """
    if not units_dir.exists():
        logger.error("Units directory does not exist: %s", units_dir)
        return 0, 0, 1

    files = sorted(os.listdir(units_dir))
    renamed_count = 0
    already_correct_count = 0
    errors_count = 0

    for filename in files:
        m = re.match(r"^(\d+)_(.*)\.png$", filename)
        if not m:
            continue

        unit_id = int(m.group(1))

        if unit_id in unit_name_map:
            unit_name = unit_name_map[unit_id]
            snake_name = to_snake_case(unit_name)
            target_filename = f"{unit_id:03d}_{snake_name}.png"

            if target_filename == filename:
                already_correct_count += 1
                continue

            src_path = units_dir / filename
            dst_path = units_dir / target_filename

            if dry_run:
                logger.info("[DRY RUN] %s -> %s (from \"%s\")", filename, target_filename, unit_name)
                renamed_count += 1
                continue

            try:
                src_path.rename(dst_path)
                logger.info("Renamed: %s -> %s (\"%s\")", filename, target_filename, unit_name)
                renamed_count += 1
            except Exception as e:
                logger.error("Error renaming %s to %s: %s", filename, target_filename, e)
                errors_count += 1

    return renamed_count, already_correct_count, errors_count


def main():
    parser = argparse.ArgumentParser(
        description="Rename unit icons in units/ using CivTechTrees JSON files."
    )
    parser.add_argument(
        "--tech-trees-dir",
        type=str,
        default="frontend/public/aoe2_assets/CivTechTrees",
        help="Path to CivTechTrees JSON directory",
    )
    parser.add_argument(
        "--units-dir",
        type=str,
        default="frontend/public/aoe2_assets/units",
        help="Path to units asset directory",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the renaming without making changes",
    )

    args = parser.parse_args()

    tech_trees_path = Path(args.tech_trees_dir).resolve()
    units_path = Path(args.units_dir).resolve()

    unit_name_map = parse_civ_tech_trees(tech_trees_path)
    renamed, unchanged, errors = rename_unit_images(
        units_dir=units_path,
        unit_name_map=unit_name_map,
        dry_run=args.dry_run,
    )

    logger.info(
        "Complete! Renamed: %d, Already Correct: %d, Errors: %d",
        renamed,
        unchanged,
        errors,
    )

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
