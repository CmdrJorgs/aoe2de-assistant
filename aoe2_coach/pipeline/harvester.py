"""
Replay and match metadata harvester: Scrapes match listings and downloads .aoe2record games into raw storage.
Supports scraping from aoe2recs.com archive via WebSocket, player profile crawling via aoe2companion,
and SQLite metadata indexing for deduplication and queries.
"""

import os
import io
import time
import zipfile
import sqlite3
import logging
import asyncio
import json
import urllib.parse
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

try:
    import websockets
except ImportError:
    websockets = None

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
    file_id: Optional[str] = None
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
                    file_id TEXT,
                    downloaded INTEGER DEFAULT 0,
                    local_file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            # Ensure file_id column exists if table existed previously without it
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(matches)")
            cols = [row[1] for row in cursor.fetchall()]
            if "file_id" not in cols:
                conn.execute("ALTER TABLE matches ADD COLUMN file_id TEXT")

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
                    winner_name, file_id, downloaded, local_file_path
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(match_id) DO UPDATE SET
                    file_id = COALESCE(excluded.file_id, matches.file_id),
                    downloaded = excluded.downloaded,
                    local_file_path = COALESCE(excluded.local_file_path, matches.local_file_path)
            """, (
                match.match_id, match.started, match.map_name, match.leaderboard,
                match.player1_name, match.player1_elo, match.player1_civ,
                match.player2_name, match.player2_elo, match.player2_civ,
                match.winner_name, match.file_id, 1 if match.downloaded else 0, match.local_file_path
            ))
            conn.commit()
            return cursor.rowcount > 0

    def get_pending_downloads(self, limit: int = 50) -> List[int]:
        """Return match IDs that have not been downloaded yet."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT match_id FROM matches WHERE downloaded = 0 LIMIT ?", (limit,))
            return [row[0] for row in cursor.fetchall()]

    def get_pending_matches(self, limit: int = 50) -> List[HarvestedMatch]:
        """Return full HarvestedMatch records for pending downloads."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT match_id, started, map_name, leaderboard,
                       player1_name, player1_elo, player1_civ,
                       player2_name, player2_elo, player2_civ,
                       winner_name, file_id, downloaded, local_file_path
                FROM matches
                WHERE downloaded = 0
                LIMIT ?
            """, (limit,))
            rows = cursor.fetchall()
            return [
                HarvestedMatch(
                    match_id=r[0],
                    started=r[1] or "",
                    map_name=r[2] or "Unknown",
                    leaderboard=r[3] or "1v1 RM",
                    player1_name=r[4] or "Player 1",
                    player1_elo=r[5] or 0,
                    player1_civ=r[6] or "Unknown",
                    player2_name=r[7] or "Player 2",
                    player2_elo=r[8] or 0,
                    player2_civ=r[9] or "Unknown",
                    winner_name=r[10],
                    file_id=r[11],
                    downloaded=bool(r[12]),
                    local_file_path=r[13],
                )
                for r in rows
            ]

    def mark_downloaded(self, match_id: int, local_file_path: str):
        """Mark a match as downloaded in the database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE matches SET downloaded = 1, local_file_path = ? WHERE match_id = ?",
                (local_file_path, match_id),
            )
            conn.commit()

    def mark_failed(self, match_id: int):
        """Mark a match as failed/unavailable in the database (downloaded = -1)."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE matches SET downloaded = -1 WHERE match_id = ?",
                (match_id,),
            )
            conn.commit()

    def count_matches(self) -> Dict[str, int]:
        """Return counts of indexed, downloaded, and failed matches."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*), SUM(CASE WHEN downloaded = 1 THEN 1 ELSE 0 END), SUM(CASE WHEN downloaded = -1 THEN 1 ELSE 0 END) FROM matches")
            row = cursor.fetchone()
            total = row[0] or 0
            downloaded = row[1] or 0
            failed = row[2] or 0
            return {"total_indexed": total, "total_downloaded": downloaded, "total_failed": failed}


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
                        file_id=None,
                        downloaded=False,
                    )
                    self.metadata_store.upsert_match(hm)
                    harvested.append(hm)

                time.sleep(self.request_delay_sec)
            except Exception as e:
                logger.error(f"Error fetching profile {pid}: {e}")

        logger.info(f"Successfully harvested {len(harvested)} matches across profiles.")
        return harvested

    async def _fetch_archive_page_async(
        self,
        ws: Any,
        page: int,
        size: int = 50,
        timeout_sec: float = 2.5,
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """Request a specific page from aoe2recs.com history WebSocket."""
        req = {"history": {"page": page, "size": size, "props": {}}}
        await ws.send(json.dumps(req))

        matches: List[Dict[str, Any]] = []
        total_count = 0

        while True:
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=timeout_sec)
                data = json.loads(msg)

                items = []
                if data.get("cls") == 3 and isinstance(data.get("data"), list):
                    items.extend(data["data"])
                else:
                    items.append(data)

                found_records = False
                for item in items:
                    if item.get("cls") == 4:  # History records
                        d = item.get("data")
                        if isinstance(d, dict):
                            total_count = d.get("total", total_count)
                            recs = d.get("records", {})
                            if isinstance(recs, dict):
                                matches.extend(recs.values())
                            elif isinstance(recs, list):
                                matches.extend(recs)
                            if recs:
                                found_records = True

                if found_records:
                    break
            except asyncio.TimeoutError:
                break

        return total_count, matches

    async def _harvest_aoe2recs_archive_async(
        self,
        max_pages: Optional[int] = None,
        page_size: int = 50,
    ) -> List[HarvestedMatch]:
        """Connect to wss://aoe2recs.com/dashboard/api/ and harvest historical match records."""
        if websockets is None:
            raise ImportError("The 'websockets' library is required to harvest from aoe2recs.com")

        uri = "wss://aoe2recs.com/dashboard/api/"
        headers = {"User-Agent": "AoE2Coach-Pipeline/1.0 (Research & Decision Support)"}
        harvested: List[HarvestedMatch] = []

        logger.info(f"Connecting to {uri} to harvest match archive...")
        async with websockets.connect(uri, additional_headers=headers) as ws:
            page = 1
            total_matches_on_server = None

            while True:
                if max_pages is not None and page > max_pages:
                    break

                logger.info(f"Fetching archive page {page} (size={page_size})...")
                total_server, raw_matches = await self._fetch_archive_page_async(
                    ws, page=page, size=page_size
                )
                if total_matches_on_server is None and total_server > 0:
                    total_matches_on_server = total_server
                    logger.info(f"Archive reports {total_matches_on_server} total recorded games available.")

                if not raw_matches:
                    logger.info(f"No matches returned for page {page}. Completed archive scrape.")
                    break

                page_harvested = 0
                for m in raw_matches:
                    mid = m.get("id")
                    if not mid:
                        continue

                    map_name = m.get("map_name") or m.get("map") or "Unknown"
                    leaderboard = m.get("game_type") or m.get("type") or "1v1 RM"
                    players = m.get("players", [])

                    p1_name = "Player 1"
                    p1_elo = 0
                    p1_civ = "Unknown"
                    p2_name = "Player 2"
                    p2_elo = 0
                    p2_civ = "Unknown"
                    winner_name = None
                    file_id = None

                    # Extract primary file_id from any player record that has one
                    for p in players:
                        fids = p.get("file_ids", [])
                        if fids and isinstance(fids, list) and len(fids) > 0:
                            file_id = str(fids[0])
                            break

                    if len(players) >= 1:
                        p1 = players[0]
                        p1_name = p1.get("name", "Player 1")
                        p1_elo = p1.get("rating") or p1.get("mmr_rm_1v1") or 0
                        p1_civ = p1.get("civilization", "Unknown")
                        if p1.get("winner"):
                            winner_name = p1_name

                    if len(players) >= 2:
                        p2 = players[1]
                        p2_name = p2.get("name", "Player 2")
                        p2_elo = p2.get("rating") or p2.get("mmr_rm_1v1") or 0
                        p2_civ = p2.get("civilization", "Unknown")
                        if p2.get("winner"):
                            winner_name = p2_name

                    hm = HarvestedMatch(
                        match_id=int(mid),
                        started=str(m.get("played", "")),
                        map_name=str(map_name),
                        leaderboard=str(leaderboard),
                        player1_name=str(p1_name),
                        player1_elo=int(p1_elo),
                        player1_civ=str(p1_civ),
                        player2_name=str(p2_name),
                        player2_elo=int(p2_elo),
                        player2_civ=str(p2_civ),
                        winner_name=winner_name,
                        file_id=file_id,
                        downloaded=False,
                    )
                    self.metadata_store.upsert_match(hm)
                    harvested.append(hm)
                    page_harvested += 1

                logger.info(f"Page {page}: indexed {page_harvested} matches. Total so far: {len(harvested)}")

                if total_matches_on_server and len(harvested) >= total_matches_on_server:
                    logger.info("Indexed all matches available in the server archive.")
                    break

                page += 1
                await asyncio.sleep(self.request_delay_sec)

        return harvested

    def harvest_aoe2recs_archive(
        self,
        max_pages: Optional[int] = None,
        page_size: int = 50,
    ) -> List[HarvestedMatch]:
        """Synchronous entrypoint to harvest matches from aoe2recs.com history archive."""
        return asyncio.run(
            self._harvest_aoe2recs_archive_async(max_pages=max_pages, page_size=page_size)
        )

    def download_replay(
        self,
        match_id: Union[int, str],
        file_id: Optional[str] = None,
    ) -> Optional[str]:
        """Download a replay file by match ID / file_id into raw storage."""
        target_path = os.path.join(self.raw_storage_dir, f"{match_id}.aoe2record")
        if os.path.exists(target_path) and os.path.getsize(target_path) > 1000:
            self.metadata_store.mark_downloaded(int(match_id), target_path)
            return target_path

        # If file_id is available, download directly from aoe2recs download API
        if file_id:
            encoded_id = urllib.parse.quote(file_id)
            url = f"https://aoe2recs.com/dashboard/api/download?id={encoded_id}"
            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code == 200 and len(resp.content) > 1000:
                    with open(target_path, "wb") as dst:
                        dst.write(resp.content)
                    self.metadata_store.mark_downloaded(int(match_id), target_path)
                    logger.info(f"Downloaded match {match_id} (size={len(resp.content)} bytes) -> {target_path}")
                    return target_path
            except Exception as e:
                logger.error(f"Error downloading match {match_id} via file_id: {e}")

        # Fallback to direct match ID endpoint
        url = f"https://aoe2recs.com/dashboard/api/download/{match_id}"
        try:
            resp = self.session.get(url, timeout=20)
            if resp.status_code == 200 and len(resp.content) > 1000:
                try:
                    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
                        namelist = z.namelist()
                        for name in namelist:
                            if name.endswith(".aoe2record"):
                                with z.open(name) as src, open(target_path, "wb") as dst:
                                    dst.write(src.read())
                                self.metadata_store.mark_downloaded(int(match_id), target_path)
                                logger.info(f"Extracted match {match_id} -> {target_path}")
                                return target_path
                except zipfile.BadZipFile:
                    with open(target_path, "wb") as dst:
                        dst.write(resp.content)
                    self.metadata_store.mark_downloaded(int(match_id), target_path)
                    logger.info(f"Downloaded raw match {match_id} -> {target_path}")
                    return target_path
        except Exception as e:
            logger.error(f"Error downloading match {match_id}: {e}")

        return None

    def download_pending_replays(
        self,
        batch_size: int = 100,
        max_downloads: Optional[int] = None,
        max_workers: int = 4,
    ) -> int:
        """Download pending recorded games in batches with multithreading."""
        total_downloaded = 0
        pending_matches = self.metadata_store.get_pending_matches(limit=batch_size)

        if not pending_matches:
            logger.info("No pending replay downloads.")
            return 0

        logger.info(f"Starting download for {len(pending_matches)} pending replays with {max_workers} workers...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_match = {
                executor.submit(self.download_replay, m.match_id, m.file_id): m
                for m in pending_matches
            }

            for future in as_completed(future_to_match):
                match = future_to_match[future]
                try:
                    res = future.result()
                    if res:
                        total_downloaded += 1
                        if max_downloads and total_downloaded >= max_downloads:
                            break
                    else:
                        self.metadata_store.mark_failed(match.match_id)
                except Exception as e:
                    logger.error(f"Exception downloading match {match.match_id}: {e}")
                    self.metadata_store.mark_failed(match.match_id)

        logger.info(f"Batch completed: downloaded {total_downloaded} replays.")
        return total_downloaded
