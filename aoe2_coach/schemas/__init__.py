"""
Schema definitions for AoE2 Coach.
"""

from aoe2_coach.schemas.game_constants import (
    Age,
    CIVILIZATIONS,
    CIV_NAME_TO_ID,
    UNIT_CATEGORIES,
    BUILDING_CATEGORIES,
    OBJECT_ID_TO_CANONICAL,
    TECH_ID_TO_CANONICAL,
    BASE_GATHER_RATES,
    UNIT_BASE_COSTS,
    BUILDING_BASE_COSTS,
    LINE_OF_SIGHT_RADII,
    get_canonical_object_name,
    get_canonical_tech_name,
    get_civ_name,
)

from aoe2_coach.schemas.match import (
    ResourceStockpile,
    VillagerAllocation,
    PlayerMetadata,
    MatchMetadata,
    PlayerState,
    SightedEntity,
    OpponentObservedState,
    TargetLabels,
    GameSnapshot,
)

__all__ = [
    "Age",
    "CIVILIZATIONS",
    "CIV_NAME_TO_ID",
    "UNIT_CATEGORIES",
    "BUILDING_CATEGORIES",
    "OBJECT_ID_TO_CANONICAL",
    "TECH_ID_TO_CANONICAL",
    "BASE_GATHER_RATES",
    "UNIT_BASE_COSTS",
    "BUILDING_BASE_COSTS",
    "LINE_OF_SIGHT_RADII",
    "get_canonical_object_name",
    "get_canonical_tech_name",
    "get_civ_name",
    "ResourceStockpile",
    "VillagerAllocation",
    "PlayerMetadata",
    "MatchMetadata",
    "PlayerState",
    "SightedEntity",
    "OpponentObservedState",
    "TargetLabels",
    "GameSnapshot",
]
