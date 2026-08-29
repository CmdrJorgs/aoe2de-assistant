#!/usr/bin/env python3
"""
Build Optimized AoE2 Asset Database (JSON and SQLite).

Parses all civilization tech tree JSONs from `frontend/public/aoe2_assets/CivTechTrees/`
and image asset directories (`units/`, `buildings/`, `tech/`).

Outputs:
1. `frontend/public/aoe2_assets/assets_db.json`
2. `frontend/public/aoe2_assets/aoe2_assets.db` (SQLite)
3. `aoe2_coach/data/assets_db.json` (for backend use)
4. `aoe2_coach/data/aoe2_assets.db` (for backend use)

Schema:
{
  "<civilization_name>": {
    "unit": {
      "<unit_key>": {
        "name": "<Display Name>",
        "image": "<png_file_location>",
        "available": true/false,
        "age_id": 1..4,
        "picture_index": 123
      }
    },
    "building": {
      "<building_key>": {
        "name": "<Display Name>",
        "image": "<png_file_location>",
        "available": true/false,
        "age_id": 1..4,
        "picture_index": 123
      }
    },
    "tech": {
      "<tech_key>": {
        "name": "<Display Name>",
        "image": "<png_file_location>",
        "available": true/false,
        "age_id": 1..4,
        "picture_index": 123
      }
    }
  }
}
"""

import argparse
import glob
import json
import logging
import os
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger("asset_db_builder")


def to_snake_case(text: str) -> str:
    """Normalize text into clean snake_case string."""
    s = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    s = re.sub(r"[\(\)\?\/]+", " ", s)
    s = re.sub(r"['\"’]+", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    return s.strip("_").lower()


def build_asset_database(
    assets_dir: Path,
) -> Dict[str, Dict[str, Dict[str, Dict[str, Any]]]]:
    """
    Build the in-memory asset database from CivTechTrees and asset directories.
    """
    civ_trees_dir = assets_dir / "CivTechTrees"
    units_dir = assets_dir / "units"
    buildings_dir = assets_dir / "buildings"
    tech_dir = assets_dir / "tech"

    # Index image files by their leading picture index ID
    unit_files: Dict[int, str] = {}
    for f in os.listdir(units_dir):
        m = re.match(r"^(\d+)_", f)
        if m and f.endswith(".png"):
            unit_files[int(m.group(1))] = f

    building_files: Dict[int, str] = {}
    for f in os.listdir(buildings_dir):
        m = re.match(r"^(\d+)_", f)
        if m and f.endswith(".png"):
            building_files[int(m.group(1))] = f

    tech_files: Dict[int, str] = {}
    for f in os.listdir(tech_dir):
        m = re.match(r"^(\d+)_", f)
        if m and f.endswith(".png"):
            tech_files[int(m.group(1))] = f

    logger.info(
        "Indexed assets: %d units, %d buildings, %d techs",
        len(unit_files),
        len(building_files),
        len(tech_files),
    )

    json_files = sorted(glob.glob(str(civ_trees_dir / "*.json")))
    logger.info("Found %d CivTechTree JSON files", len(json_files))

    db: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}
    global_units: Dict[str, Dict[str, Any]] = {}
    global_buildings: Dict[str, Dict[str, Any]] = {}
    global_techs: Dict[str, Dict[str, Any]] = {}

    for jf in json_files:
        civ_raw = Path(jf).stem
        civ_key = to_snake_case(civ_raw)

        with open(jf, "r", encoding="utf-8") as f:
            data = json.load(f)

        civ_entry: Dict[str, Dict[str, Dict[str, Any]]] = {
            "unit": {},
            "building": {},
            "tech": {},
        }

        # 1. Process buildings list
        for b in data.get("civ_techs_buildings", []):
            name = b.get("Name")
            pic = b.get("Picture Index")
            if name and pic is not None and pic in building_files:
                b_key = to_snake_case(name)
                img_path = f"/aoe2_assets/buildings/{building_files[pic]}"
                is_avail = b.get("Node Status") != "NotAvailable"
                item_obj = {
                    "name": name,
                    "image": img_path,
                    "available": is_avail,
                    "age_id": b.get("Age ID"),
                    "picture_index": pic,
                    "node_id": b.get("Node ID"),
                }
                civ_entry["building"][b_key] = item_obj
                if b_key not in global_buildings or is_avail:
                    global_buildings[b_key] = item_obj

        # 2. Process units & techs list
        for item in data.get("civ_techs_units", []):
            name = item.get("Name")
            pic = item.get("Picture Index")
            ut = item.get("Use Type")
            if not name or pic is None:
                continue

            item_key = to_snake_case(name)
            is_avail = item.get("Node Status") != "NotAvailable"

            if ut == "Unit" and pic in unit_files:
                img_path = f"/aoe2_assets/units/{unit_files[pic]}"
                item_obj = {
                    "name": name,
                    "image": img_path,
                    "available": is_avail,
                    "age_id": item.get("Age ID"),
                    "picture_index": pic,
                    "node_id": item.get("Node ID"),
                }
                civ_entry["unit"][item_key] = item_obj
                if item_key not in global_units or is_avail:
                    global_units[item_key] = item_obj

            elif ut == "Tech" and pic in tech_files:
                img_path = f"/aoe2_assets/tech/{tech_files[pic]}"
                item_obj = {
                    "name": name,
                    "image": img_path,
                    "available": is_avail,
                    "age_id": item.get("Age ID"),
                    "picture_index": pic,
                    "node_id": item.get("Node ID"),
                }
                civ_entry["tech"][item_key] = item_obj
                if item_key not in global_techs or is_avail:
                    global_techs[item_key] = item_obj

            elif ut == "Building" and pic in building_files:
                img_path = f"/aoe2_assets/buildings/{building_files[pic]}"
                item_obj = {
                    "name": name,
                    "image": img_path,
                    "available": is_avail,
                    "age_id": item.get("Age ID"),
                    "picture_index": pic,
                    "node_id": item.get("Node ID"),
                }
                civ_entry["building"][item_key] = item_obj
                if item_key not in global_buildings or is_avail:
                    global_buildings[item_key] = item_obj

        db[civ_key] = civ_entry

    # 3. Add all remaining named units / assets into universal '_all' civ entry
    # (includes campaign heroes, resources, environmental icons)
    for pic, fname in unit_files.items():
        # Parse name from filename e.g. 001_knight.png -> knight
        m = re.match(r"^\d+_(.*)\.png$", fname)
        if m and not m.group(1).startswith("50730"):
            item_key = m.group(1)
            raw_title = item_key.replace("_", " ").title()
            if item_key not in global_units:
                global_units[item_key] = {
                    "name": raw_title,
                    "image": f"/aoe2_assets/units/{fname}",
                    "available": True,
                    "picture_index": pic,
                }

    for pic, fname in building_files.items():
        m = re.match(r"^\d+_(.*)\.png$", fname)
        if m:
            item_key = m.group(1)
            raw_title = item_key.replace("_", " ").title()
            if item_key not in global_buildings:
                global_buildings[item_key] = {
                    "name": raw_title,
                    "image": f"/aoe2_assets/buildings/{fname}",
                    "available": True,
                    "picture_index": pic,
                }

    for pic, fname in tech_files.items():
        m = re.match(r"^\d+_(.*)\.png$", fname)
        if m:
            item_key = m.group(1)
            raw_title = item_key.replace("_", " ").title()
            if item_key not in global_techs:
                global_techs[item_key] = {
                    "name": raw_title,
                    "image": f"/aoe2_assets/tech/{fname}",
                    "available": True,
                    "picture_index": pic,
                }

    db["_all"] = {
        "unit": global_units,
        "building": global_buildings,
        "tech": global_techs,
    }

    return db


def export_sqlite_database(
    db: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]],
    sqlite_path: Path,
) -> None:
    """
    Export the asset database to SQLite with optimized indexes.
    """
    sqlite_path.parent.mkdir(parents=True, exist_ok=True)
    if sqlite_path.exists():
        sqlite_path.unlink()

    conn = sqlite3.connect(str(sqlite_path))
    cursor = conn.cursor()

    # Enable WAL mode for high read concurrency
    cursor.execute("PRAGMA journal_mode = WAL;")
    cursor.execute("PRAGMA synchronous = NORMAL;")

    cursor.execute(
        """
        CREATE TABLE assets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            civ TEXT NOT NULL,
            category TEXT NOT NULL,       -- 'unit', 'building', 'tech'
            item_key TEXT NOT NULL,       -- snake_case identifier e.g. 'knight'
            name TEXT NOT NULL,           -- Display name e.g. 'Knight'
            image TEXT NOT NULL,          -- Web image path e.g. '/aoe2_assets/units/001_knight.png'
            available INTEGER NOT NULL,   -- 1 = Available, 0 = Not Available
            age_id INTEGER,               -- 1 = Dark, 2 = Feudal, 3 = Castle, 4 = Imperial
            picture_index INTEGER,        -- Engine picture / frame index
            node_id INTEGER
        );
        """
    )

    cursor.execute("CREATE INDEX idx_assets_civ_cat_key ON assets (civ, category, item_key);")
    cursor.execute("CREATE INDEX idx_assets_civ_cat ON assets (civ, category);")
    cursor.execute("CREATE INDEX idx_assets_cat_key ON assets (category, item_key);")
    cursor.execute("CREATE INDEX idx_assets_name ON assets (name);")

    records = []
    for civ, categories in db.items():
        for category, items in categories.items():
            for item_key, data in items.items():
                records.append(
                    (
                        civ,
                        category,
                        item_key,
                        data.get("name", ""),
                        data.get("image", ""),
                        1 if data.get("available", True) else 0,
                        data.get("age_id"),
                        data.get("picture_index"),
                        data.get("node_id"),
                    )
                )

    cursor.executemany(
        """
        INSERT INTO assets (civ, category, item_key, name, image, available, age_id, picture_index, node_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
        """,
        records,
    )

    conn.commit()
    conn.close()
    logger.info("Exported %d records to SQLite database: %s", len(records), sqlite_path)


def main():
    parser = argparse.ArgumentParser(
        description="Build optimized JSON and SQLite asset databases for AoE2."
    )
    parser.add_argument(
        "--assets-dir",
        type=str,
        default="frontend/public/aoe2_assets",
        help="Path to frontend/public/aoe2_assets directory",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="frontend/public/aoe2_assets/assets_db.json",
        help="Path for output JSON database",
    )
    parser.add_argument(
        "--output-sqlite",
        type=str,
        default="frontend/public/aoe2_assets/aoe2_assets.db",
        help="Path for output SQLite database",
    )

    args = parser.parse_args()
    assets_path = Path(args.assets_dir).resolve()

    logger.info("Building asset database from %s", assets_path)
    db = build_asset_database(assets_path)

    # 1. Save frontend public JSON
    json_path = Path(args.output_json).resolve()
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    logger.info("Saved JSON database (%d civs) to %s", len(db), json_path)

    # 2. Save backend copies if data directory exists
    backend_data_dir = Path("aoe2_coach/data").resolve()
    backend_data_dir.mkdir(parents=True, exist_ok=True)
    backend_json_path = backend_data_dir / "assets_db.json"
    with open(backend_json_path, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)
    logger.info("Saved backend JSON copy to %s", backend_json_path)

    # 3. Save SQLite database
    sqlite_path = Path(args.output_sqlite).resolve()
    export_sqlite_database(db, sqlite_path)

    backend_sqlite_path = backend_data_dir / "aoe2_assets.db"
    export_sqlite_database(db, backend_sqlite_path)

    logger.info("Asset database build successfully completed!")


if __name__ == "__main__":
    main()
