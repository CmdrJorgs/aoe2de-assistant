"""
Pydantic Schemas for AoE2 Match Data, Player State, Fog-of-War Sighted State, and Snapshots.
"""

from typing import List, Dict, Optional, Tuple, Any
from pydantic import BaseModel, Field
from aoe2_coach.schemas.game_constants import Age, get_civ_name


class ResourceStockpile(BaseModel):
    food: int = Field(default=0, ge=0, description="Current food stockpile")
    wood: int = Field(default=0, ge=0, description="Current wood stockpile")
    gold: int = Field(default=0, ge=0, description="Current gold stockpile")
    stone: int = Field(default=0, ge=0, description="Current stone stockpile")


class VillagerAllocation(BaseModel):
    total: int = Field(default=0, ge=0, description="Total active villagers")
    food: int = Field(default=0, ge=0, description="Villagers gathering food (farms/sheep/berries/hunt)")
    wood: int = Field(default=0, ge=0, description="Villagers chopping wood")
    gold: int = Field(default=0, ge=0, description="Villagers mining gold")
    stone: int = Field(default=0, ge=0, description="Villagers mining stone")
    idle_rate: float = Field(default=0.0, ge=0.0, le=1.0, description="Estimated idle percentage (0.0 to 1.0)")


class PlayerMetadata(BaseModel):
    player_id: int
    name: str
    civ_id: int
    civ_name: str
    elo: Optional[int] = None
    winner: bool = False
    color_id: int = 1
    human: bool = True
    eapm: Optional[int] = None


class MatchMetadata(BaseModel):
    match_id: str
    patch_version: str
    map_id: Optional[int] = None
    map_name: str = "Unknown"
    duration_sec: float
    diplomacy: str = "1v1"
    game_type: str = "Random Map"
    speed: str = "Normal (1.7x)"
    winning_player_id: Optional[int] = None
    players: List[PlayerMetadata] = Field(default_factory=list)


class PlayerState(BaseModel):
    player_id: int = Field(default=1, description="Player in-game ID (1-8)")
    civ_id: int
    civ_name: str
    elo: Optional[int] = None
    age: int = Field(default=1, ge=1, le=4, description="Age (1=Dark, 2=Feudal, 3=Castle, 4=Imperial)")
    age_name: str = "Dark Age"
    resources: ResourceStockpile = Field(default_factory=ResourceStockpile)
    villagers: VillagerAllocation = Field(default_factory=VillagerAllocation)
    military_units: Dict[str, int] = Field(default_factory=dict, description="Active counts of military units")
    buildings: Dict[str, int] = Field(default_factory=dict, description="Active counts of buildings")
    completed_techs: List[str] = Field(default_factory=list, description="Researched technologies")


class SightedEntity(BaseModel):
    entity_name: str
    entity_type: str = Field(description="'unit' or 'building'")
    count: int = Field(default=1, ge=1)
    last_seen_sec: float = Field(description="Timestamp in seconds when entity was last seen")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Decayed observation confidence")
    position: Optional[Tuple[float, float]] = None


class OpponentObservedState(BaseModel):
    civ_id: int
    civ_name: str
    estimated_age: int = Field(default=1, ge=1, le=4)
    estimated_age_name: str = "Dark Age"
    sighted_units: List[SightedEntity] = Field(default_factory=list)
    sighted_buildings: List[SightedEntity] = Field(default_factory=list)


class TargetLabels(BaseModel):
    winner: bool
    next_unit_produced: Optional[str] = None
    next_tech_researched: Optional[str] = None
    next_building_built: Optional[str] = None
    primary_composition_next_5m: Optional[str] = None
    action_vector_next_5m: Dict[str, int] = Field(default_factory=dict)


class GameSnapshot(BaseModel):
    match_id: str
    patch_version: str
    timestamp_sec: int
    map_type: str
    player: PlayerState
    opponent_observed: OpponentObservedState
    label: TargetLabels

    def to_flat_dict(self) -> Dict[str, Any]:
        """Flatten snapshot into a flat dictionary suitable for Parquet / DataFrame export."""
        flat = {
            "match_id": self.match_id,
            "patch_version": self.patch_version,
            "timestamp_sec": self.timestamp_sec,
            "map_type": self.map_type,
            # Player fields
            "player_civ_id": self.player.civ_id,
            "player_civ_name": self.player.civ_name,
            "player_elo": self.player.elo or 0,
            "player_age": self.player.age,
            "player_food": self.player.resources.food,
            "player_wood": self.player.resources.wood,
            "player_gold": self.player.resources.gold,
            "player_stone": self.player.resources.stone,
            "player_vills_total": self.player.villagers.total,
            "player_vills_food": self.player.villagers.food,
            "player_vills_wood": self.player.villagers.wood,
            "player_vills_gold": self.player.villagers.gold,
            "player_vills_stone": self.player.villagers.stone,
            "player_military_total": sum(self.player.military_units.values()),
            "player_tech_count": len(self.player.completed_techs),
            # Opponent observed fields
            "opponent_civ_id": self.opponent_observed.civ_id,
            "opponent_civ_name": self.opponent_observed.civ_name,
            "opponent_estimated_age": self.opponent_observed.estimated_age,
            "opponent_sighted_units_count": sum(u.count for u in self.opponent_observed.sighted_units),
            "opponent_sighted_buildings_count": sum(b.count for b in self.opponent_observed.sighted_buildings),
            # Labels
            "label_winner": self.label.winner,
            "label_next_unit": self.label.next_unit_produced or "none",
            "label_next_tech": self.label.next_tech_researched or "none",
            "label_next_building": self.label.next_building_built or "none",
            "label_primary_comp": self.label.primary_composition_next_5m or "none",
        }
        return flat
