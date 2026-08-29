#!/usr/bin/env python3
"""
Convert and Rename AoE2 Unit Icons.

This script processes unit icon images in `frontend/public/aoe2_assets/units/`.
1. Scrapes or parses unit names corresponding to their Icon ID from
   https://agecommunity.fandom.com/wiki/Icon_ID.
2. Converts DDS images to standard PNG format using Pillow (PIL).
3. Renames each image from its in-game ID hash (e.g. `001_50730.DDS`) to its
   proper snake_case unit name (e.g. `001_knight.png`).
4. Cleans up the original DDS files upon successful conversion.
"""

import argparse
import logging
import os
import re
import sys
import unicodedata
import urllib.request
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image
from bs4 import BeautifulSoup

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("unit_converter")

# Fallback unit map matching https://agecommunity.fandom.com/wiki/Icon_ID
FALLBACK_UNIT_MAP: Dict[int, str] = {
    0: "Dead Fish Trap",
    1: "Knight",
    2: "Paladin",
    3: "Deer",
    4: "Fish",
    5: "Hawk",
    6: "Forage Bush",
    7: "Wolf",
    8: "Militia",
    9: "Stone Mine",
    10: "Man-at-Arms",
    11: "Pikeman",
    12: "Two-handed Swordsman",
    13: "Long Swordsman",
    14: "Gold Mine",
    15: "Male Villager",
    16: "Female Villager",
    17: "Archer",
    18: "Crossbowman",
    19: "Cavalry archer",
    20: "Skirmisher",
    21: "Elite Skirmisher",
    22: "Hand Cannoneer",
    23: "Trade Cog",
    24: "Fishing Ship",
    25: "War Galley",
    26: "Relic",
    27: "Mangonel",
    28: "Trebuchet (unpacked)",
    29: "Trebuchet (packed)",
    30: "Bombard Cannon",
    31: "Spearman",
    32: "Tree",
    33: "Monk",
    34: "Trade Cart",
    35: "Cataphract",
    36: "Chu Ko Nu",
    37: "Mameluke",
    38: "Berserk",
    39: "Janissary",
    40: "Longboat",
    41: "Longbowman",
    42: "Manguadi",
    43: "War Elephant",
    44: "Samurai",
    45: "Teutonic Knight",
    46: "Throwing Axeman",
    47: "Woad Raider",
    48: "King",
    49: "Cavalier",
    50: "Huskarl",
    51: "La Hire",
    52: "Joan the Maid",
    53: "Subotai",
    54: "Ghengis Khan",
    55: "Cannon Galleon",
    56: "Guy Joesslyne",
    57: "Emperor in a Barrel",
    58: "Petard",
    59: "Sieur de Metz",
    60: "Galleon",
    61: "Sieur Bertrand",
    62: "Franksih Paladin",
    63: "Capped Ram",
    64: "Scout Cavalry",
    65: "Duke D'Alençon",
    66: "Lord de Graville",
    67: "Jean de Lorrain",
    68: "Jean Bureau",
    69: "Sir John Fastolf",
    70: "Reynald de Chatillon",
    71: "Heavy Cavalry Archer",
    72: "Champion",
    73: "Siege Ram",
    74: "Battering Ram",
    75: "Alexander Nevski",
    76: "Joan of Arc",
    77: "Archers of the Eyes",
    78: "Camel",
    79: "Heavy Camel",
    80: "Kushluk",
    81: "Scorpion",
    82: "Shah",
    83: "Heavy Demolition Ship",
    84: "Demolition Ship",
    85: "Fast Fire Ship",
    86: "Fire Ship",
    87: "Galley",
    88: "William Wallace",
    89: "Heavy Scorpion",
    90: "Arbalest",
    91: "Light Cavalry",
    92: "Richard the Lionhearted",
    93: "Empty (94)",
    94: "Bad Neighbor/God's Own Sling (unpacked)",
    95: "Transport Ship",
    96: "Sheep",
    97: "Idle Villager Button (??)",
    98: "Boar/Javelina",
    99: "Dolphin (unused)",
    100: "Bad Neighbor/God's Own Sling (packed)",
    101: "Onager",
    102: "Siege Onager",
    103: "Hussar",
    104: "Halberdier",
    105: "Tarkan",
    106: "Conquistador",
    107: "Missionary",
    108: "Plumed Archer",
    109: "Eagle Warrior",
    110: "Jaguar Warrior",
    111: "Jaguar",
    112: "Horse",
    113: "Petard",
    114: "Eagle Warrior (technology)",
    115: "Turkey",
    116: "Turtle Ship",
    117: "War Wagon",
    118: "Erik the Red/El Cid",
    119: "Attila the Hun",
    120: "leda the Hun",
    121: "Scythian Wild Woman",
    122: "Imam",
    123: "King Alfonso",
    124: "King Sancho",
    125: "Henry V",
    126: "Minamoto",
    127: "Admiral Yi Sun Shin",
    128: "William the Conqueror",
    129: "Charles Martel",
    130: "Pope Leo I",
    131: "Monk (American)",
    132: "Furious the Monkey Boy",
    133: "Stormy Dog",
}


def to_snake_case(text: str) -> str:
    """Convert raw wiki unit label to clean snake_case string."""
    # Normalize unicode accents (e.g. Alençon -> Alencon)
    s = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    # Replace punctuation that separates words with spaces
    s = re.sub(r"[\(\)\?\/]+", " ", s)
    # Remove apostrophes and quotes
    s = re.sub(r"['\"’]+", "", s)
    # Replace non-alphanumeric characters with underscore
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    s = s.strip("_").lower()
    return s


def fetch_wiki_unit_map(url: str) -> Dict[int, str]:
    """Scrape the wiki page to obtain the map of Icon ID -> Unit Name."""
    try:
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"},
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode("utf-8", errors="ignore")

        soup = BeautifulSoup(html, "html.parser")
        content_div = soup.find("div", class_="mw-parser-output")
        if not content_div:
            logger.warning("Could not find 'mw-parser-output' div in wiki HTML. Using fallback.")
            return FALLBACK_UNIT_MAP

        units_p = None
        for p in content_div.find_all("p"):
            if p.get_text().strip() == "Units":
                units_p = p
                break

        if not units_p:
            logger.warning("Could not find 'Units' header in wiki page. Using fallback.")
            return FALLBACK_UNIT_MAP

        ul = units_p.find_next_sibling("ul")
        if not ul:
            logger.warning("Could not find units list <ul> element. Using fallback.")
            return FALLBACK_UNIT_MAP

        unit_map: Dict[int, str] = {}
        for li in ul.find_all("li"):
            text = li.get_text().strip()
            m = re.match(r"^(\d+)\s*-\s*(.*)$", text)
            if m:
                uid = int(m.group(1))
                name = m.group(2).strip()
                unit_map[uid] = name

        logger.info("Successfully parsed %d unit names from wiki: %s", len(unit_map), url)
        return unit_map
    except Exception as e:
        logger.warning("Failed to fetch wiki page (%s). Using fallback map. Error: %s", url, e)
        return FALLBACK_UNIT_MAP


def process_units(
    units_dir: Path,
    unit_map: Dict[int, str],
    dry_run: bool = False,
    keep_dds: bool = False,
) -> Tuple[int, int, int]:
    """
    Convert all DDS unit images in units_dir to PNG and rename them using snake_case names.

    Returns:
        Tuple of (converted_count, renamed_with_wiki_name_count, errors_count)
    """
    if not units_dir.exists():
        logger.error("Units directory does not exist: %s", units_dir)
        return 0, 0, 1

    files = sorted(os.listdir(units_dir))
    converted_count = 0
    wiki_named_count = 0
    errors_count = 0

    logger.info("Found %d total files in %s", len(files), units_dir)

    for filename in files:
        # Match files like 000_50730.DDS or 001_50730.dds
        m = re.match(r"^(\d+)_([^\.]+)\.(dds|DDS)$", filename)
        if not m:
            continue

        unit_id = int(m.group(1))
        src_path = units_dir / filename

        if unit_id in unit_map:
            raw_name = unit_map[unit_id]
            snake_name = to_snake_case(raw_name)
            dst_filename = f"{unit_id:03d}_{snake_name}.png"
            wiki_named_count += 1
        else:
            # Fallback for IDs beyond the classic wiki list (e.g. 134..756)
            dst_filename = f"{unit_id:03d}_{m.group(2)}.png"

        dst_path = units_dir / dst_filename

        if dry_run:
            logger.info("[DRY RUN] %s -> %s", filename, dst_filename)
            converted_count += 1
            continue

        try:
            with Image.open(src_path) as img:
                # Ensure image is in RGBA mode for PNG transparency
                if img.mode != "RGBA":
                    img = img.convert("RGBA")
                img.save(dst_path, format="PNG")

            converted_count += 1

            if not keep_dds:
                src_path.unlink()

        except Exception as e:
            logger.error("Error processing %s: %s", filename, e)
            errors_count += 1

    return converted_count, wiki_named_count, errors_count


def main():
    parser = argparse.ArgumentParser(
        description="Convert DDS unit icons to PNG and rename to snake_case unit names."
    )
    parser.add_argument(
        "--units-dir",
        type=str,
        default="frontend/public/aoe2_assets/units",
        help="Path to units asset directory (default: frontend/public/aoe2_assets/units)",
    )
    parser.add_argument(
        "--wiki-url",
        type=str,
        default="https://agecommunity.fandom.com/wiki/Icon_ID",
        help="Wiki URL with Icon ID mapping",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate the renaming and conversion without making changes",
    )
    parser.add_argument(
        "--keep-dds",
        action="store_true",
        help="Keep original DDS files after converting to PNG",
    )

    args = parser.parse_args()

    units_path = Path(args.units_dir).resolve()
    logger.info("Target units directory: %s", units_path)

    unit_map = fetch_wiki_unit_map(args.wiki_url)
    logger.info("Loaded unit map with %d entries.", len(unit_map))

    converted, wiki_named, errors = process_units(
        units_dir=units_path,
        unit_map=unit_map,
        dry_run=args.dry_run,
        keep_dds=args.keep_dds,
    )

    logger.info(
        "Complete! Converted: %d, Renamed with Wiki Names: %d, Errors: %d",
        converted,
        wiki_named,
        errors,
    )

    if errors > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
