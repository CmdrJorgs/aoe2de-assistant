"""
AoE2: Definitive Edition Patch 101.102.x Ruleset.
Encodes the baseline 45 civilizations (Britons to Georgians), standard gather rates,
and baseline combat damage mechanics.
"""

from typing import Dict, List, Optional, Set, Any, Union
from aoe2_coach.schemas.game_constants import Age, CIVILIZATIONS, CIV_NAME_TO_ID, BASE_GATHER_RATES
from aoe2_coach.rules.game_ruleset import GameRuleset
from aoe2_coach.rules.tech_tree import CIVILIZATIONS_DATABASE, CivInfo, TECHS_DATABASE


# Baseline 45 Civilization Strategic Archetype Profiles
BASELINE_CIV_ARCHETYPES: Dict[str, Dict[str, float]] = {
    # Cavalry civs
    "franks": {"cavalry": 1.0, "archer": 0.2, "infantry": 0.5, "siege": 0.4, "monk": 0.2},
    "magyars": {"cavalry": 1.0, "archer": 0.8, "infantry": 0.3, "siege": 0.2, "monk": 0.2},
    "huns": {"cavalry": 1.0, "archer": 0.8, "infantry": 0.2, "siege": 0.3, "monk": 0.1},
    "berbers": {"cavalry": 1.0, "archer": 0.4, "infantry": 0.2, "siege": 0.3, "monk": 0.4},
    "cumans": {"cavalry": 1.0, "archer": 0.6, "infantry": 0.3, "siege": 0.6, "monk": 0.1},
    "lithuanians": {"cavalry": 1.0, "archer": 0.4, "infantry": 0.5, "siege": 0.3, "monk": 0.8},
    "bulgarians": {"cavalry": 0.9, "archer": 0.2, "infantry": 0.9, "siege": 0.8, "monk": 0.3},
    "tatars": {"cavalry": 0.9, "archer": 0.9, "infantry": 0.2, "siege": 0.7, "monk": 0.2},
    "poles": {"cavalry": 0.9, "archer": 0.4, "infantry": 0.6, "siege": 0.4, "monk": 0.6},
    "burgundians": {"cavalry": 0.9, "archer": 0.3, "infantry": 0.4, "siege": 0.5, "monk": 0.5},
    "persians": {"cavalry": 0.9, "archer": 0.5, "infantry": 0.3, "siege": 0.5, "monk": 0.3},
    "gurjaras": {"cavalry": 1.0, "archer": 0.2, "infantry": 0.3, "siege": 0.3, "monk": 0.4},
    "georgians": {"cavalry": 0.9, "archer": 0.2, "infantry": 0.4, "siege": 0.6, "monk": 0.5},
    # Archer civs
    "britons": {"cavalry": 0.2, "archer": 1.0, "infantry": 0.4, "siege": 0.4, "monk": 0.3},
    "mayans": {"cavalry": 0.0, "archer": 1.0, "infantry": 0.8, "siege": 0.5, "monk": 0.4},
    "ethiopians": {"cavalry": 0.3, "archer": 1.0, "infantry": 0.4, "siege": 0.8, "monk": 0.3},
    "vietnamese": {"cavalry": 0.4, "archer": 1.0, "infantry": 0.3, "siege": 0.4, "monk": 0.3},
    "italians": {"cavalry": 0.4, "archer": 0.9, "infantry": 0.5, "siege": 0.4, "monk": 0.6},
    "chinese": {"cavalry": 0.7, "archer": 0.9, "infantry": 0.7, "siege": 0.6, "monk": 0.5},
    "koreans": {"cavalry": 0.2, "archer": 0.9, "infantry": 0.3, "siege": 0.9, "monk": 0.5},
    "dravidians": {"cavalry": 0.0, "archer": 0.9, "infantry": 0.8, "siege": 0.8, "monk": 0.3},
    # Infantry civs
    "goths": {"cavalry": 0.4, "archer": 0.2, "infantry": 1.0, "siege": 0.3, "monk": 0.2},
    "japanese": {"cavalry": 0.5, "archer": 0.7, "infantry": 1.0, "siege": 0.4, "monk": 0.6},
    "vikings": {"cavalry": 0.4, "archer": 0.7, "infantry": 1.0, "siege": 0.5, "monk": 0.3},
    "aztecs": {"cavalry": 0.0, "archer": 0.8, "infantry": 1.0, "siege": 0.7, "monk": 1.0},
    "incas": {"cavalry": 0.0, "archer": 0.8, "infantry": 1.0, "siege": 0.5, "monk": 0.6},
    "celts": {"cavalry": 0.4, "archer": 0.3, "infantry": 0.9, "siege": 1.0, "monk": 0.3},
    "malians": {"cavalry": 0.7, "archer": 0.6, "infantry": 0.9, "siege": 0.5, "monk": 0.6},
    "romans": {"cavalry": 0.6, "archer": 0.4, "infantry": 1.0, "siege": 0.7, "monk": 0.3},
    "armenians": {"cavalry": 0.4, "archer": 0.7, "infantry": 0.9, "siege": 0.6, "monk": 0.9},
    # Camel / Counter / Monk civs
    "byzantines": {"cavalry": 0.7, "archer": 0.7, "infantry": 0.7, "siege": 0.5, "monk": 0.8},
    "saracens": {"cavalry": 0.8, "archer": 0.8, "infantry": 0.3, "siege": 0.7, "monk": 0.8},
    "hindustanis": {"cavalry": 0.9, "archer": 0.6, "infantry": 0.5, "siege": 0.5, "monk": 0.4},
    "turks": {"cavalry": 0.8, "archer": 0.9, "infantry": 0.2, "siege": 0.8, "monk": 0.3},
    "bohemians": {"cavalry": 0.2, "archer": 0.7, "infantry": 0.6, "siege": 1.0, "monk": 0.9},
    "bengalis": {"cavalry": 0.6, "archer": 0.6, "infantry": 0.4, "siege": 0.6, "monk": 0.9},
    "slavs": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.8, "siege": 0.9, "monk": 0.7},
    "teutons": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.8, "siege": 0.8, "monk": 0.8},
    "portuguese": {"cavalry": 0.6, "archer": 0.7, "infantry": 0.5, "siege": 0.8, "monk": 0.7},
    "spanish": {"cavalry": 0.8, "archer": 0.3, "infantry": 0.5, "siege": 0.5, "monk": 0.9},
    "burmese": {"cavalry": 0.8, "archer": 0.2, "infantry": 0.9, "siege": 0.5, "monk": 0.9},
    "khmer": {"cavalry": 0.8, "archer": 0.5, "infantry": 0.3, "siege": 0.9, "monk": 0.4},
    "malay": {"cavalry": 0.3, "archer": 0.8, "infantry": 0.8, "siege": 0.5, "monk": 0.6},
    "mongols": {"cavalry": 0.9, "archer": 0.9, "infantry": 0.3, "siege": 0.8, "monk": 0.3},
}

DEFAULT_ARCHETYPE = {"cavalry": 0.5, "archer": 0.5, "infantry": 0.5, "siege": 0.5, "monk": 0.5}


class Patch101_102_Ruleset(GameRuleset):
    """
    Implementation of the baseline 45-civilization ruleset (Patch 101.102.x).
    """
    patch_version = "101.102.x"
    display_name = "Definitive Edition (Patch 101.102.x)"

    def __init__(self):
        self._civs = dict(CIVILIZATIONS)
        self._civ_name_to_id = dict(CIV_NAME_TO_ID)
        self._civ_archetypes = dict(BASELINE_CIV_ARCHETYPES)
        self._gather_rates = dict(BASE_GATHER_RATES)
        self._elevation_advantage = 0.25
        self._civ_db = dict(CIVILIZATIONS_DATABASE)

    @property
    def civilizations(self) -> Dict[int, str]:
        return self._civs

    @property
    def civ_name_to_id(self) -> Dict[str, int]:
        return self._civ_name_to_id

    @property
    def civ_archetypes(self) -> Dict[str, Dict[str, float]]:
        return self._civ_archetypes

    @property
    def base_gather_rates(self) -> Dict[str, float]:
        return self._gather_rates

    @property
    def elevation_advantage(self) -> float:
        return self._elevation_advantage

    def get_civ_info(self, civ: Union[str, int]) -> Optional[CivInfo]:
        if isinstance(civ, int):
            cname = self._civs.get(civ, "").lower()
        else:
            cname = str(civ).lower().strip()
        return self._civ_db.get(cname)

    def is_unit_available(self, civ: Union[str, int], unit_id: str, age: Optional[Age] = None) -> bool:
        info = self.get_civ_info(civ)
        if not info:
            return False  # Unknown civ in this patch
        unit_id_clean = unit_id.lower().strip()
        if unit_id_clean in info.disabled_units:
            return False
        from aoe2_coach.rules.units import get_unit_stats
        stats = get_unit_stats(unit_id_clean)
        if stats and stats.is_unique:
            return unit_id_clean in [u.lower() for u in info.unique_units]
        return True

    def is_tech_available(self, civ: Union[str, int], tech_id: str, age: Optional[Age] = None) -> bool:
        info = self.get_civ_info(civ)
        if not info:
            return False
        tech_id_clean = tech_id.lower().strip()
        return tech_id_clean not in info.disabled_techs

    def is_building_available(self, civ: Union[str, int], building_id: str) -> bool:
        info = self.get_civ_info(civ)
        if not info:
            return False
        b_clean = building_id.lower().strip()
        return b_clean not in info.disabled_buildings
