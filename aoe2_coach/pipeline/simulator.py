"""
Game state reconstructor and simulator for AoE2:DE matches over continuous time.
Reconstructs player economy, villager distribution, military army, buildings, and technology state.
"""

from typing import Dict, List, Optional, Tuple, Set
import copy

from aoe2_coach.schemas.game_constants import (
    Age,
    BASE_GATHER_RATES,
    UNIT_BASE_COSTS,
    BUILDING_BASE_COSTS,
    UNIT_CATEGORIES,
    BUILDING_CATEGORIES,
)
from aoe2_coach.schemas.match import (
    PlayerState,
    ResourceStockpile,
    VillagerAllocation,
    PlayerMetadata,
    MatchMetadata,
)
from aoe2_coach.pipeline.parser import (
    ParsedReplayData,
    GameEvent,
    TrainEvent,
    ResearchEvent,
    BuildEvent,
    MoveEvent,
    InteractEvent,
    ResignEvent,
)


class PlayerStateTracker:
    """Tracks and simulates a single player's game state over time."""

    def __init__(self, metadata: PlayerMetadata):
        self.player_id = metadata.player_id
        self.civ_id = metadata.civ_id
        self.civ_name = metadata.civ_name
        self.elo = metadata.elo
        self.winner = metadata.winner

        # State variables
        self.current_time_sec = 0.0
        self.age = Age.DARK
        
        # Initial starting economy
        food, wood, gold, stone = self._get_starting_resources()
        self.resources = {
            "food": float(food),
            "wood": float(wood),
            "gold": float(gold),
            "stone": float(stone),
        }

        # Initial starting units & buildings
        initial_vills = 6 if self.civ_name.lower() == "chinese" else (4 if self.civ_name.lower() == "mayans" else 3)
        self.vills_food = initial_vills
        self.vills_wood = 0
        self.vills_gold = 0
        self.vills_stone = 0

        self.military_units: Dict[str, int] = {}
        # Starting scout
        if self.civ_name.lower() in ["aztecs", "mayans", "incas"]:
            self.military_units["eagle_scout"] = 1
        else:
            self.military_units["scout_cavalry"] = 1

        self.buildings: Dict[str, int] = {
            "town_center": 1,
        }
        self.completed_techs: Set[str] = set()

    def _get_starting_resources(self) -> Tuple[int, int, int, int]:
        """Apply civ bonuses to starting resources."""
        civ_lower = self.civ_name.lower()
        food, wood, gold, stone = 200, 200, 100, 200
        if civ_lower == "chinese":
            food += 150
            wood += 50
        elif civ_lower == "mayans":
            food -= 50
        elif civ_lower == "huns":
            wood -= 100
        elif civ_lower == "persians":
            food += 50
            wood += 50
        elif civ_lower == "lithuanians":
            food += 150
        return food, wood, gold, stone

    def advance_time(self, target_time_sec: float):
        """Advance time and simulate resource gathering between current_time_sec and target_time_sec."""
        dt = target_time_sec - self.current_time_sec
        if dt <= 0:
            return

        # Eco tech multipliers
        wood_multiplier = 1.10 if "double_bit_axe" in self.completed_techs else 1.0
        if "bow_saw" in self.completed_techs:
            wood_multiplier *= 1.10
        if "two_man_saw" in self.completed_techs:
            wood_multiplier *= 1.10

        farm_multiplier = 1.08 if "wheelbarrow" in self.completed_techs else 1.0
        if "hand_cart" in self.completed_techs:
            farm_multiplier *= 1.08

        gold_multiplier = 1.15 if "gold_mining" in self.completed_techs else 1.0
        if "gold_shaft_mining" in self.completed_techs:
            gold_multiplier *= 1.15

        stone_multiplier = 1.15 if "stone_mining" in self.completed_techs else 1.0
        if "stone_shaft_mining" in self.completed_techs:
            stone_multiplier *= 1.15

        # Gather rates
        food_rate = BASE_GATHER_RATES["food_farm"] * farm_multiplier
        wood_rate = BASE_GATHER_RATES["wood"] * wood_multiplier
        gold_rate = BASE_GATHER_RATES["gold"] * gold_multiplier
        stone_rate = BASE_GATHER_RATES["stone"] * stone_multiplier

        self.resources["food"] += self.vills_food * food_rate * dt
        self.resources["wood"] += self.vills_wood * wood_rate * dt
        self.resources["gold"] += self.vills_gold * gold_rate * dt
        self.resources["stone"] += self.vills_stone * stone_rate * dt

        self.current_time_sec = target_time_sec

    def apply_event(self, event: GameEvent):
        """Update player state based on an in-game event."""
        self.advance_time(event.timestamp_sec)

        if isinstance(event, TrainEvent):
            uname = event.canonical_name
            if uname == "villager":
                # Intelligently allocate new villager based on current age & eco balance
                total_vills = self.vills_food + self.vills_wood + self.vills_gold + self.vills_stone
                if total_vills < 6:
                    self.vills_food += 1
                elif total_vills < 10:
                    self.vills_wood += 1
                elif total_vills < 14:
                    self.vills_food += 1
                elif total_vills < 18:
                    self.vills_gold += 1
                else:
                    # Allocate based on current deficit
                    if self.resources["wood"] < 150:
                        self.vills_wood += 1
                    elif self.resources["food"] < 200:
                        self.vills_food += 1
                    elif self.resources["gold"] < 150:
                        self.vills_gold += 1
                    else:
                        self.vills_food += 1
            else:
                self.military_units[uname] = self.military_units.get(uname, 0) + event.amount

            # Deduct costs
            cost = UNIT_BASE_COSTS.get(uname, (50, 0, 0, 0))
            self.resources["food"] = max(0.0, self.resources["food"] - cost[0] * event.amount)
            self.resources["wood"] = max(0.0, self.resources["wood"] - cost[1] * event.amount)
            self.resources["gold"] = max(0.0, self.resources["gold"] - cost[2] * event.amount)
            self.resources["stone"] = max(0.0, self.resources["stone"] - cost[3] * event.amount)

        elif isinstance(event, BuildEvent):
            bname = event.canonical_name
            self.buildings[bname] = self.buildings.get(bname, 0) + 1

            # Adjust villager tasks if relevant building is constructed
            if bname == "farm":
                # Shift a woodchopper to farm if available
                if self.vills_wood > 4:
                    self.vills_wood -= 1
                    self.vills_food += 1
            elif bname == "mining_camp":
                # Shift 2 woodchoppers to gold or stone
                if self.vills_wood > 6:
                    self.vills_wood -= 2
                    self.vills_gold += 2

            # Deduct costs
            cost = BUILDING_BASE_COSTS.get(bname, (0, 100, 0, 0))
            self.resources["food"] = max(0.0, self.resources["food"] - cost[0])
            self.resources["wood"] = max(0.0, self.resources["wood"] - cost[1])
            self.resources["gold"] = max(0.0, self.resources["gold"] - cost[2])
            self.resources["stone"] = max(0.0, self.resources["stone"] - cost[3])

        elif isinstance(event, ResearchEvent):
            tname = event.canonical_name
            self.completed_techs.add(tname)

            if tname == "feudal_age" or event.tech_id == 101:
                self.age = max(self.age, Age.FEUDAL)
            elif tname == "castle_age" or event.tech_id == 102:
                self.age = max(self.age, Age.CASTLE)
            elif tname == "imperial_age" or event.tech_id == 103:
                self.age = max(self.age, Age.IMPERIAL)

    def to_player_state(self) -> PlayerState:
        """Export current state snapshot to Pydantic PlayerState schema."""
        total_vills = self.vills_food + self.vills_wood + self.vills_gold + self.vills_stone
        return PlayerState(
            player_id=self.player_id,
            civ_id=self.civ_id,
            civ_name=self.civ_name,
            elo=self.elo,
            age=int(self.age),
            age_name=self.age.display_name,
            resources=ResourceStockpile(
                food=int(self.resources["food"]),
                wood=int(self.resources["wood"]),
                gold=int(self.resources["gold"]),
                stone=int(self.resources["stone"]),
            ),
            villagers=VillagerAllocation(
                total=total_vills,
                food=self.vills_food,
                wood=self.vills_wood,
                gold=self.vills_gold,
                stone=self.vills_stone,
                idle_rate=0.02,
            ),
            military_units=dict(self.military_units),
            buildings=dict(self.buildings),
            completed_techs=sorted(list(self.completed_techs)),
        )


class GameStateSimulator:
    """Simulates multi-player match states across continuous time from parsed replay events."""

    def __init__(self, parsed_data: ParsedReplayData):
        self.metadata = parsed_data.metadata
        self.events = parsed_data.events
        self.trackers: Dict[int, PlayerStateTracker] = {}

        for player_meta in self.metadata.players:
            self.trackers[player_meta.player_id] = PlayerStateTracker(player_meta)

        self._event_idx = 0
        self._current_sim_time = 0.0

    def step_to_time(self, target_time_sec: float) -> Dict[int, PlayerState]:
        """Advance the simulation up to `target_time_sec` and return each player's state."""
        # Process all events up to target_time_sec
        while self._event_idx < len(self.events):
            ev = self.events[self._event_idx]
            if ev.timestamp_sec > target_time_sec:
                break

            pid = ev.player_id
            if pid in self.trackers:
                self.trackers[pid].apply_event(ev)

            self._event_idx += 1

        # Advance remaining time for all players
        for tracker in self.trackers.values():
            tracker.advance_time(target_time_sec)

        self._current_sim_time = target_time_sec

        return {pid: tracker.to_player_state() for pid, tracker in self.trackers.items()}
