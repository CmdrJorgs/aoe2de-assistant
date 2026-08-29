"""
AoE2 Asset Database Manager.

Provides fast, indexed access to civilization unit, building, and tech image paths
and metadata using either JSON or SQLite backend.
"""

import json
import logging
import os
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("asset_db")

_DB_CACHE: Optional[Dict[str, Any]] = None


def normalize_asset_key(text: str) -> str:
    """Normalize text into clean snake_case string."""
    s = unicodedata.normalize("NFKD", text).encode("ASCII", "ignore").decode("utf-8")
    s = re.sub(r"[\(\)\?\/]+", " ", s)
    s = re.sub(r"['\"’]+", "", s)
    s = re.sub(r"[^a-zA-Z0-9]+", "_", s)
    return s.strip("_").lower()


class AssetDatabase:
    """In-memory and SQLite-backed asset database client."""

    def __init__(self, json_path: Optional[str] = None, sqlite_path: Optional[str] = None):
        self.base_dir = Path(__file__).resolve().parent.parent.parent
        self.json_path = (
            Path(json_path)
            if json_path
            else self.base_dir / "aoe2_coach" / "data" / "assets_db.json"
        )
        self.sqlite_path = (
            Path(sqlite_path)
            if sqlite_path
            else self.base_dir / "aoe2_coach" / "data" / "aoe2_assets.db"
        )
        self._data: Optional[Dict[str, Any]] = None

    def load(self) -> Dict[str, Any]:
        """Load JSON database into memory with caching."""
        global _DB_CACHE
        if _DB_CACHE is not None:
            self._data = _DB_CACHE
            return self._data

        if self.json_path.exists():
            with open(self.json_path, "r", encoding="utf-8") as f:
                self._data = json.load(f)
                _DB_CACHE = self._data
                return self._data

        logger.warning("Asset database JSON not found at %s", self.json_path)
        self._data = {}
        return self._data

    def get_asset(
        self,
        name_or_key: str,
        category: str = "unit",
        civ: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Get asset dictionary for a specific name/category/civ.
        """
        data = self.load()
        key = normalize_asset_key(name_or_key)
        civ_key = normalize_asset_key(civ) if civ else "_all"

        # 1. Check civ-specific category
        if civ_key in data and category in data[civ_key] and key in data[civ_key][category]:
            return data[civ_key][category][key]

        # 2. Check global '_all'
        if "_all" in data and category in data["_all"] and key in data["_all"][category]:
            return data["_all"][category][key]

        return None

    def get_unit_image(self, name_or_key: str, civ: Optional[str] = None) -> Optional[str]:
        """Get PNG image web path for a unit."""
        asset = self.get_asset(name_or_key, category="unit", civ=civ)
        return asset.get("image") if asset else None

    def get_building_image(self, name_or_key: str, civ: Optional[str] = None) -> Optional[str]:
        """Get PNG image web path for a building."""
        asset = self.get_asset(name_or_key, category="building", civ=civ)
        return asset.get("image") if asset else None

    def get_tech_image(self, name_or_key: str, civ: Optional[str] = None) -> Optional[str]:
        """Get PNG image web path for a technology."""
        asset = self.get_asset(name_or_key, category="tech", civ=civ)
        return asset.get("image") if asset else None

    def query_sqlite(
        self,
        category: Optional[str] = None,
        civ: Optional[str] = None,
        available_only: bool = True,
    ) -> List[Dict[str, Any]]:
        """Perform optimized relational query using SQLite database."""
        if not self.sqlite_path.exists():
            return []

        conn = sqlite3.connect(str(self.sqlite_path))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()

        query = "SELECT * FROM assets WHERE 1=1"
        params: List[Any] = []

        if civ:
            query += " AND civ = ?"
            params.append(normalize_asset_key(civ))
        if category:
            query += " AND category = ?"
            params.append(category.lower())
        if available_only:
            query += " AND available = 1"

        query += " ORDER BY age_id ASC, name ASC"

        c.execute(query, params)
        rows = [dict(row) for row in c.fetchall()]
        conn.close()
        return rows


# Global singleton instance
default_asset_db = AssetDatabase()
