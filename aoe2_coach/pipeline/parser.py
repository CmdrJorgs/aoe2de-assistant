"""
Replay binary parser wrapping aoe2rec-py with structured event decoding and metadata extraction.
"""

import os
import struct
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union

from aoe2rec_py import RecSummary
from aoe2rec_py.aoe2rec_py import parse_rec
import mgz.reference

from aoe2_coach.schemas.game_constants import (
    get_canonical_object_name,
    get_canonical_tech_name,
    get_civ_name,
)
from aoe2_coach.schemas.match import MatchMetadata, PlayerMetadata

logger = logging.getLogger(__name__)


@dataclass
class BaseGameEvent:
    timestamp_sec: float
    player_id: int


@dataclass
class TrainEvent(BaseGameEvent):
    unit_id: int
    canonical_name: str
    amount: int
    building_type: int


@dataclass
class ResearchEvent(BaseGameEvent):
    tech_id: int
    canonical_name: str
    building_id: int


@dataclass
class BuildEvent(BaseGameEvent):
    building_id: int
    canonical_name: str
    x: float
    y: float


@dataclass
class MoveEvent(BaseGameEvent):
    unit_ids: List[int]
    x: float
    y: float


@dataclass
class InteractEvent(BaseGameEvent):
    unit_ids: List[int]
    target_id: int
    x: float
    y: float


@dataclass
class ChatEvent(BaseGameEvent):
    message: str


@dataclass
class ResignEvent(BaseGameEvent):
    pass


@dataclass
class ViewlockEvent(BaseGameEvent):
    x: float
    y: float


GameEvent = Union[
    TrainEvent,
    ResearchEvent,
    BuildEvent,
    MoveEvent,
    InteractEvent,
    ChatEvent,
    ResignEvent,
    ViewlockEvent,
]


@dataclass
class ParsedReplayData:
    metadata: MatchMetadata
    events: List[GameEvent] = field(default_factory=list)
    map_size: int = 120
    raw_operation_count: int = 0


class ReplayParser:
    """Parser for AoE2:DE recorded game binary files."""

    def __init__(self):
        try:
            self._ref_dataset = mgz.reference.get_dataset(mgz.reference.Version.DE, 0)[1]
        except Exception:
            self._ref_dataset = {}

    def parse_file(self, filepath: str) -> ParsedReplayData:
        """Parse a recorded game from a file path."""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Replay file not found: {filepath}")

        with open(filepath, "rb") as f:
            raw_bytes = f.read()

        match_id = os.path.splitext(os.path.basename(filepath))[0]
        # Clean potential prefix like SD-AgeIIDE_Replay_
        if "_" in match_id:
            match_id = match_id.split("_")[-1]

        return self.parse_bytes(raw_bytes, match_id=match_id)

    def parse_bytes(self, raw_bytes: bytes, match_id: Optional[str] = None) -> ParsedReplayData:
        """Parse raw recorded game bytes into structured metadata and chronologically ordered events."""
        if not raw_bytes:
            raise ValueError("Replay raw bytes cannot be empty")

        match_id = match_id or "unknown_match"

        # 1. Extract high-level summary metadata
        metadata = self._extract_metadata(raw_bytes, match_id)

        # 2. Parse binary operation stream
        parsed_rec = parse_rec(raw_bytes)
        operations = parsed_rec.get("operations", [])
        events: List[GameEvent] = []

        for op in operations:
            if "Action" in op:
                action = op["Action"]
                wt_ms = action.get("world_time", 0)
                t_sec = max(0.0, wt_ms / 1000.0)
                adata = action.get("action_data", {})

                if "DeQueue" in adata:
                    dq = adata["DeQueue"]
                    pid = dq.get("player_id", 0)
                    uid = dq.get("unit_id", 0)
                    btype = dq.get("building_type", 0)
                    amount = dq.get("amount", 1)
                    events.append(
                        TrainEvent(
                            timestamp_sec=t_sec,
                            player_id=pid,
                            unit_id=uid,
                            canonical_name=get_canonical_object_name(uid, "unit"),
                            amount=amount,
                            building_type=btype,
                        )
                    )

                elif "Research" in adata:
                    r = adata["Research"]
                    pid = r.get("player_id", 0)
                    tid = r.get("technology_type", 0)
                    bid = r.get("building_id", 0)
                    events.append(
                        ResearchEvent(
                            timestamp_sec=t_sec,
                            player_id=pid,
                            tech_id=tid,
                            canonical_name=get_canonical_tech_name(tid),
                            building_id=bid,
                        )
                    )

                elif "Build" in adata:
                    b = adata["Build"]
                    pid = b.get("player_id", 0)
                    bdata = bytes(b.get("data", []))
                    if len(bdata) >= 16:
                        try:
                            x, y, bid = struct.unpack("<ffI", bdata[4:16])
                            events.append(
                                BuildEvent(
                                    timestamp_sec=t_sec,
                                    player_id=pid,
                                    building_id=bid,
                                    canonical_name=get_canonical_object_name(bid, "building"),
                                    x=float(x),
                                    y=float(y),
                                )
                            )
                        except Exception as e:
                            logger.debug(f"Failed to unpack Build event: {e}")

                elif "Move" in adata:
                    m = adata["Move"]
                    pid = m.get("player_id", 0)
                    unit_ids = m.get("unit_ids", [])
                    x = float(m.get("x", 0.0))
                    y = float(m.get("y", 0.0))
                    events.append(
                        MoveEvent(
                            timestamp_sec=t_sec,
                            player_id=pid,
                            unit_ids=unit_ids,
                            x=x,
                            y=y,
                        )
                    )

                elif "Interact" in adata:
                    inter = adata["Interact"]
                    pid = inter.get("player_id", 0)
                    unit_ids = inter.get("unit_ids", [])
                    target_id = inter.get("target_id", 0)
                    x = float(inter.get("x", 0.0))
                    y = float(inter.get("y", 0.0))
                    events.append(
                        InteractEvent(
                            timestamp_sec=t_sec,
                            player_id=pid,
                            unit_ids=unit_ids,
                            target_id=target_id,
                            x=x,
                            y=y,
                        )
                    )

                elif "Resign" in adata:
                    res = adata["Resign"]
                    pid = res.get("player_id", 0)
                    events.append(ResignEvent(timestamp_sec=t_sec, player_id=pid))

            elif "Chat" in op:
                chat = op["Chat"]
                # Sometimes chat is a dict or string
                msg = ""
                pid = 0
                if isinstance(chat, dict):
                    msg = chat.get("message", "") or chat.get("text", "")
                    pid = chat.get("player", 0)
                elif isinstance(chat, str):
                    msg = chat
                events.append(ChatEvent(timestamp_sec=0.0, player_id=pid, message=str(msg)))

        # Sort events chronologically
        events.sort(key=lambda e: e.timestamp_sec)

        # Extract map size from zheader if available
        map_size = 120
        zh = parsed_rec.get("zheader")
        if isinstance(zh, dict):
            gs = zh.get("game_settings", {})
            if isinstance(gs, dict):
                map_size = gs.get("map_size", 120) or 120

        return ParsedReplayData(
            metadata=metadata,
            events=events,
            map_size=map_size,
            raw_operation_count=len(operations),
        )

    def _extract_metadata(self, raw_bytes: bytes, match_id: str) -> MatchMetadata:
        """Extract MatchMetadata from raw bytes using RecSummary and reference dataset."""
        import io

        summary = RecSummary(io.BytesIO(raw_bytes))
        raw_players = summary.get_players()
        duration = summary.get_duration()
        duration_sec = duration.total_seconds() if duration else 0.0
        diplomacy = summary.get_diplomacy()
        diplomacy_str = diplomacy.get("type", "1v1") if isinstance(diplomacy, dict) else "1v1"
        version_info = summary.get_version()
        patch_str = f"{version_info[0]}_{version_info[1]}_build_{version_info[4]}" if version_info else "DE_Unknown"

        players: List[PlayerMetadata] = []
        winner_id: Optional[int] = None

        for p in raw_players:
            pid = p.get("number", 1)
            cid = p.get("civilization", 0)
            civ_name = get_civ_name(cid)
            is_winner = bool(p.get("winner", False))
            if is_winner:
                winner_id = pid

            players.append(
                PlayerMetadata(
                    player_id=pid,
                    name=p.get("name", f"Player {pid}"),
                    civ_id=cid,
                    civ_name=civ_name,
                    elo=p.get("rate_snapshot"),
                    winner=is_winner,
                    color_id=p.get("color_id", pid),
                    human=bool(p.get("human", True)),
                    eapm=p.get("eapm"),
                )
            )

        # Map name extraction
        map_name = "Arabia"
        try:
            parsed_rec = parse_rec(raw_bytes)
            zh = parsed_rec.get("zheader", {})
            if isinstance(zh, dict):
                gs = zh.get("game_settings", {})
                if isinstance(gs, dict):
                    mid = gs.get("selected_map_id") or gs.get("resolved_map_id")
                    if mid is not None and self._ref_dataset:
                        maps_dict = self._ref_dataset.get("maps", {})
                        if str(mid) in maps_dict:
                            map_name = maps_dict[str(mid)]
        except Exception:
            pass

        return MatchMetadata(
            match_id=match_id,
            patch_version=patch_str,
            duration_sec=duration_sec,
            diplomacy=diplomacy_str,
            winning_player_id=winner_id,
            players=players,
            map_name=map_name,
        )
