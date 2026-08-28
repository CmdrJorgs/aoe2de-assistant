"""
Fog-of-War and Line-of-Sight (LOS) Simulator.
Simulates partial observability, player field-of-view, sighted opponent entity memory, and observation decay.
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass, field

from aoe2_coach.schemas.game_constants import (
    Age,
    LINE_OF_SIGHT_RADII,
    UNIT_CATEGORIES,
    BUILDING_CATEGORIES,
)
from aoe2_coach.schemas.match import (
    SightedEntity,
    OpponentObservedState,
    PlayerMetadata,
)
from aoe2_coach.pipeline.parser import (
    GameEvent,
    TrainEvent,
    BuildEvent,
    MoveEvent,
    InteractEvent,
    ParsedReplayData,
)


@dataclass
class EntityLocation:
    entity_id: int
    player_id: int
    name: str
    entity_type: str  # "unit" or "building"
    x: float
    y: float
    los_radius: float
    last_update_sec: float
    active: bool = True


class PlayerFogOfWarTracker:
    """Tracks what a specific player has observed regarding an opponent."""

    def __init__(self, player_id: int, opponent_metadata: PlayerMetadata, decay_half_life_sec: float = 120.0):
        self.player_id = player_id
        self.opponent_id = opponent_metadata.player_id
        self.opponent_civ_id = opponent_metadata.civ_id
        self.opponent_civ_name = opponent_metadata.civ_name
        self.decay_half_life_sec = decay_half_life_sec
        self.decay_constant = math.log(2) / decay_half_life_sec

        # Sighted memory: mapping entity canonical name -> SightedEntity
        self.sighted_units: Dict[str, SightedEntity] = {}
        self.sighted_buildings: Dict[str, SightedEntity] = {}
        self.inferred_enemy_age = Age.DARK

    def sight_enemy_entity(
        self,
        name: str,
        entity_type: str,
        x: float,
        y: float,
        timestamp_sec: float,
        count: int = 1,
    ):
        """Record that an enemy entity was directly observed by this player."""
        # Age inference based on sighted entity
        self._infer_age_from_entity(name)

        if entity_type == "unit":
            if name not in self.sighted_units:
                self.sighted_units[name] = SightedEntity(
                    entity_name=name,
                    entity_type="unit",
                    count=count,
                    last_seen_sec=timestamp_sec,
                    confidence=1.0,
                    position=(x, y),
                )
            else:
                existing = self.sighted_units[name]
                # Update with latest observed count and timestamp
                existing.count = max(existing.count, count)
                existing.last_seen_sec = timestamp_sec
                existing.confidence = 1.0
                existing.position = (x, y)

        elif entity_type == "building":
            if name not in self.sighted_buildings:
                self.sighted_buildings[name] = SightedEntity(
                    entity_name=name,
                    entity_type="building",
                    count=count,
                    last_seen_sec=timestamp_sec,
                    confidence=1.0,
                    position=(x, y),
                )
            else:
                existing = self.sighted_buildings[name]
                existing.count = max(existing.count, count)
                existing.last_seen_sec = timestamp_sec
                existing.confidence = 1.0
                existing.position = (x, y)

    def _infer_age_from_entity(self, name: str):
        """Infer enemy age based on sighted units or buildings."""
        castle_age_entities = {
            "knight", "cavalier", "crossbowman", "heavy_camel_rider",
            "castle", "monastery", "siege_workshop", "university",
            "mangonel", "scorpion", "monk", "camel_rider", "cavalry_archer",
        }
        imperial_age_entities = {
            "paladin", "arbalester", "trebuchet", "bombard_cannon",
            "hand_cannoneer", "siege_ram", "siege_onager", "heavy_scorpion",
            "bombard_tower", "wonder", "feitoria",
        }

        if name in imperial_age_entities:
            self.inferred_enemy_age = max(self.inferred_enemy_age, Age.IMPERIAL)
        elif name in castle_age_entities:
            self.inferred_enemy_age = max(self.inferred_enemy_age, Age.CASTLE)
        elif name in {"archery_range", "stable", "blacksmith", "market", "fish_trap", "watch_tower"}:
            self.inferred_enemy_age = max(self.inferred_enemy_age, Age.FEUDAL)

    def get_observed_state(self, current_time_sec: float) -> OpponentObservedState:
        """Return decayed observed state of the opponent at current_time_sec."""
        active_units: List[SightedEntity] = []
        for name, record in self.sighted_units.items():
            dt = max(0.0, current_time_sec - record.last_seen_sec)
            confidence = math.exp(-self.decay_constant * dt)
            # Only include units sighted with non-trivial confidence
            if confidence > 0.05:
                active_units.append(
                    SightedEntity(
                        entity_name=name,
                        entity_type="unit",
                        count=record.count,
                        last_seen_sec=record.last_seen_sec,
                        confidence=round(confidence, 3),
                        position=record.position,
                    )
                )

        # Buildings do not decay rapidly (they are stationary)
        active_buildings: List[SightedEntity] = []
        for name, record in self.sighted_buildings.items():
            active_buildings.append(
                SightedEntity(
                    entity_name=name,
                    entity_type="building",
                    count=record.count,
                    last_seen_sec=record.last_seen_sec,
                    confidence=1.0,
                    position=record.position,
                )
            )

        return OpponentObservedState(
            civ_id=self.opponent_civ_id,
            civ_name=self.opponent_civ_name,
            estimated_age=int(self.inferred_enemy_age),
            estimated_age_name=self.inferred_enemy_age.display_name,
            sighted_units=active_units,
            sighted_buildings=active_buildings,
        )


class FogOfWarEngine:
    """Manages spatial locations of entities and simulates line-of-sight checks between players."""

    def __init__(self, parsed_data: ParsedReplayData):
        self.metadata = parsed_data.metadata
        self.events = parsed_data.events
        self.entities: Dict[int, EntityLocation] = {}
        self._next_synthetic_id = 100000

        # Create FoW trackers for each player vs opponent
        self.trackers: Dict[int, PlayerFogOfWarTracker] = {}
        players = self.metadata.players
        if len(players) >= 2:
            p1, p2 = players[0], players[1]
            self.trackers[p1.player_id] = PlayerFogOfWarTracker(p1.player_id, p2)
            self.trackers[p2.player_id] = PlayerFogOfWarTracker(p2.player_id, p1)
        elif len(players) == 1:
            p1 = players[0]
            self.trackers[p1.player_id] = PlayerFogOfWarTracker(p1.player_id, p1)

        self._event_idx = 0
        self._current_sim_time = 0.0

    def step_to_time(self, target_time_sec: float) -> Dict[int, OpponentObservedState]:
        """Process events up to target_time_sec and compute current FoW observations."""
        while self._event_idx < len(self.events):
            ev = self.events[self._event_idx]
            if ev.timestamp_sec > target_time_sec:
                break

            self._process_event(ev)
            self._event_idx += 1

        self._current_sim_time = target_time_sec

        # Return observed state for each player
        return {
            pid: tracker.get_observed_state(target_time_sec)
            for pid, tracker in self.trackers.items()
        }

    def _process_event(self, ev: GameEvent):
        """Update spatial positions and perform LOS checks for an event."""
        pid = ev.player_id

        if isinstance(ev, BuildEvent):
            b_id = self._next_synthetic_id
            self._next_synthetic_id += 1
            b_name = ev.canonical_name
            los = LINE_OF_SIGHT_RADII.get(b_name, 4.0)

            ent = EntityLocation(
                entity_id=b_id,
                player_id=pid,
                name=b_name,
                entity_type="building",
                x=ev.x,
                y=ev.y,
                los_radius=los,
                last_update_sec=ev.timestamp_sec,
            )
            self.entities[b_id] = ent

            # Check if opponent sees this building being constructed
            for other_pid, tracker in self.trackers.items():
                if other_pid != pid:
                    if self._is_position_visible_to_player(ev.x, ev.y, other_pid):
                        tracker.sight_enemy_entity(b_name, "building", ev.x, ev.y, ev.timestamp_sec)

        elif isinstance(ev, MoveEvent):
            # Update unit positions
            for uid in ev.unit_ids:
                if uid in self.entities:
                    self.entities[uid].x = ev.x
                    self.entities[uid].y = ev.y
                    self.entities[uid].last_update_sec = ev.timestamp_sec
                else:
                    # New discovered entity ID
                    self.entities[uid] = EntityLocation(
                        entity_id=uid,
                        player_id=pid,
                        name="scout_cavalry",
                        entity_type="unit",
                        x=ev.x,
                        y=ev.y,
                        los_radius=LINE_OF_SIGHT_RADII.get("scout_cavalry", 6.0),
                        last_update_sec=ev.timestamp_sec,
                    )

                # Check if this moving unit enters opponent's line-of-sight
                for other_pid, tracker in self.trackers.items():
                    if other_pid != pid:
                        if self._is_position_visible_to_player(ev.x, ev.y, other_pid):
                            tracker.sight_enemy_entity(
                                self.entities[uid].name, "unit", ev.x, ev.y, ev.timestamp_sec
                            )

        elif isinstance(ev, InteractEvent):
            # Combat / interaction reveals position to both players
            for other_pid, tracker in self.trackers.items():
                if other_pid != pid:
                    tracker.sight_enemy_entity("military_unit", "unit", ev.x, ev.y, ev.timestamp_sec)

        elif isinstance(ev, TrainEvent):
            # When unit trains, create a synthetic unit at player base
            uid = self._next_synthetic_id
            self._next_synthetic_id += 1
            u_name = ev.canonical_name
            los = LINE_OF_SIGHT_RADII.get(u_name, 4.0)
            self.entities[uid] = EntityLocation(
                entity_id=uid,
                player_id=pid,
                name=u_name,
                entity_type="unit",
                x=0.0,
                y=0.0,
                los_radius=los,
                last_update_sec=ev.timestamp_sec,
            )

    def _is_position_visible_to_player(self, target_x: float, target_y: float, player_id: int) -> bool:
        """Check if target coordinates are within any of player's entities' line-of-sight radii."""
        for ent in self.entities.values():
            if ent.player_id == player_id and ent.active:
                dx = ent.x - target_x
                dy = ent.y - target_y
                dist_sq = dx * dx + dy * dy
                if dist_sq <= ent.los_radius * ent.los_radius:
                    return True
        return False
