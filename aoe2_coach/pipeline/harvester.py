"""
Replay and match metadata harvester: Scrapes match listings and downloads .aoe2record games into raw storage.
Includes SQLite metadata index for deduplication and filtered queries (by ELO tier, civs, maps).
"""

import os
import io
import time
import zipfile
import sqlite3
import logging
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass

import requests

logger = logging.getLogger(__name__)

# Representative pro & community player profile IDs to seed match crawling
SEED_PRO_PROFILE_IDS = [
    196240,   # TheViper
    198034,   # Hera
    210609,   # Liereyy
    263176,   # TaToH
    1762409,  # Kei
    3816609,  # iamkaito
    254972,   # DauT
    198889,   # Jordan
    209525,   # Villese
    240394,   # Yo
    409742,   # Sitaux
    199325,   # TheMax
]


@dataclass
class HarvestedMatch:
    match_id: int
    started: str
    map_name: str
    leaderboard: str
    player1_name: str
    player1_elo: int
    player1_civ: str
    player2_name: str
    player2_elo: int
    player2_civ: str
    winner_name: Optional[str]
    downloaded: bool = False
    local_file_path: Optional[str] = None


class MetadataStore:
    """SQLite-backed metadata index for scraped AoE2 matches and replays."""

    def __init__(self, db_path: str = "data/metadata/matches.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS matches (
                    match_id INTEGER PRIMARY KEY,
                    started TEXT,
                    map_name TEXT,
                    leaderboard TEXT,
                    player1_name TEXT,
                    player1_elo INTEGER,
                    player1_civ TEXT,
                    player2_name TEXT,
                    player2_elo INTEGER,
                    player2_civ TEXT,
                    winner_name TEXT,
                    downloaded INTEGER DEFAULT 0,
                    local_file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_elo1 ON matches(player1_elo)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_map ON matches(map_name)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_downloaded ON matches(downloaded)")
            conn.commit()

    def upsert_match(self, match: HarvestedMatch) -> bool:
        """Insert match or update if already present."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO matches (
                    match_id, started, map_name, leaderboard,
                    player1_name, player1_elo, player1_civ,
                    player2_name, player2_elo, player2_civ,
                    winner_name, downloaded, local_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    downloaded = excluded.downloaded,
                    local_file_path = COALESCE(excluded.local_file_path, matches.local_file_path)
            """, (
                match.match_id, match.started, match.map_name, match.leaderboard,
                match.player1_name, match.player1_elo, match.player1_civ,
                match.player2_name, match.player2_elo, match.player2_civ,
                match.winner_name, 1 if match.downloaded else 0, match.local_file_path
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_pending_downloads(self, limit: int = 50) -> List[int]:
        """Return match IDs that have not been downloaded yet."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT match_id FROM matches WHERE downloaded = 0 LIMIT ?", (limit,))
            return [row[0] for row in cursor.fetchall()]

    def count_matches(self) -> Dict[str, int]:
        """Return counts of indexed and downloaded matches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(downloaded) FROM matches")
            row = cursor.fetchone()
            total = row[0] or 0
            downloaded = row[1] or 0
            return {"total_indexed": total, "total_downloaded": downloaded}


class ReplayHarvester:
    """Scrapes match histories from public endpoints and downloads recorded games."""

    def __init__(
        self,
        raw_storage_dir: str = "data/raw",
        metadata_db_path: str = "data/metadata/matches.db",
        request_delay_sec: float = 0.5,
    ):
        self.raw_storage_dir = raw_storage_dir
        self.metadata_store = MetadataStore(metadata_db_path)
        self.request_delay_sec = request_delay_sec
        os.makedirs(self.raw_storage_dir, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "AoE2Coach-Pipeline/1.0 (Research & Player Decision Support Engine)"
        })

    def harvest_matches_for_profiles(
        self,
        profile_ids: Optional[List[int]] = None,
        count_per_profile: int = 20,
    ) -> List[HarvestedMatch]:
        """Fetch match histories for given player profile IDs and record them in the metadata store."""
        profiles = profile_ids or SEED_PRO_PROFILE_IDS
        harvested: List[HarvestedMatch] = []

        logger.info(f"Harvesting match lists for {len(profiles)} profiles...")

        for pid in profiles:
            url = f"https://data.aoe2companion.com/api/matches?profile_ids={pid}&count={count_per_profile}"
            try:
                resp = self.session.get(url, timeout=10)
                if resp.status_code != 200:
                    logger.warning(f"Failed to fetch matches for profile {pid}: HTTP {resp.status_code}")
                    continue

                data = resp.json()
                matches = data.get("matches", [])
                for m in matches:
                    teams = m.get("teams", [])
                    if len(teams) != 2:
                        continue  # Focus on 1v1

                    p1_list = teams[0].get("players", [])
                    p2_list = teams[1].get("players", [])
                    if not p1_list or not p2_list:
                        continue

                    p1 = p1_list[0]
                    p2 = p2_list[0]

                    winner_name = p1.get("name") if p1.get("won") else (p2.get("name") if p2.get("won") else None)

                    hm = HarvestedMatch(
                        match_id=m["matchId"],
                        started=m.get("started", ""),
                        map_name=m.get("mapName", "Unknown"),
                        leaderboard=m.get("leaderboardName", "1v1 RM"),
                        player1_name=p1.get("name", "Player 1"),
                        player1_elo=p1.get("rating") or 0,
                        player1_civ=p1.get("civName", "Unknown"),
                        player2_name=p2.get("name", "Player 2"),
                        player2_elo=p2.get("rating") or 0,
                        player2_civ=p2.get("civName", "Unknown"),
                        winner_name=winner_name,
                        downloaded=False,
                    )
                    self.metadata_store.upsert_match(hm)
                    harvested.append(hm)

                time.sleep(self.request_delay_sec)
            except Exception as e:
                logger.error(f"Error fetching profile {pid}: {e}")

        logger.info(f"Successfully harvested {len(harvested)} matches across profiles.")
        return harvested

    def download_replay(self, match_id: Union[int, str]) -> Optional[str]:
        """Download a replay file by match ID into raw storage."""
        target_path = os.path.join(self.raw_storage_dir, f"{match_id}.aoe2record")
        if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
            return target_path

        url = f"https://aoe2recs.com/dashboard/api/download/{match_id}"
        try:
            resp = self.session.get(url, timeout=15)
            if resp.status_code == 200 and len(resp.content) > 100:
                # Often returned as a zip containing the .aoe2record
                try:
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                        namelist = z.namelist()
                        for name in namelist:
                            if name.endswith(".aoe2record"):
                                with z.open(name) as src, open(target_path, "wb") as dst:
                                    dst.write(src.read())
                                logger.info(f"Downloaded and extracted match {match_id} -> {target_path}")
                                return target_path
                except zipfile.BadZipFile:
                    # Direct raw record bytes
                    with open(target_path, "wb") as dst:
                        dst.write(resp.content)
                    return target_path
            else:
                logger.debug(f"Replay {match_id} not available on server (size={len(resp.content)} bytes).")
        except Exception as e:
            logger.error(f"Error downloading match {match_id}: {e}")

        return None
