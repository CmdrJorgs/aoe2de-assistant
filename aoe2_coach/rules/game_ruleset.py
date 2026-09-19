"""
AoE2 Versioned Game Ruleset Interface & Rules Registry.
Provides clean encapsulation and version boundaries for civilizations, unit statistics,
tech trees, gather rates, and core combat mechanics.
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Set, Any, Union
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.rules.units import UnitStats, ResourceCost


class GameRuleset(ABC):
    """
    Abstract representation of an AoE2:DE game balance and version state.
    """
    patch_version: str
    display_name: str

    @property
    @abstractmethod
    def civilizations(self) -> Dict[int, str]:
        """Mapping of civ ID -> display name."""
        pass

    @property
    @abstractmethod
    def civ_name_to_id(self) -> Dict[str, int]:
        """Mapping of lowercase civ name -> ID."""
        pass

    @property
    @abstractmethod
    def civ_archetypes(self) -> Dict[str, Dict[str, float]]:
        """Strategic archetype affinities for ML feature extraction."""
        pass

    @property
    @abstractmethod
    def base_gather_rates(self) -> Dict[str, float]:
        """Base gather rates per resource type (resources/sec/villager)."""
        pass

    @property
    @abstractmethod
    def elevation_advantage(self) -> float:
        """Standard high ground damage multiplier (e.g. 0.25 for +25%)."""
        pass

    @abstractmethod
    def get_civ_info(self, civ: Union[str, int]) -> Optional[Any]:
        """Get CivInfo object for a civilization."""
        pass

    @abstractmethod
    def is_unit_available(self, civ: Union[str, int], unit_id: str, age: Optional[Age] = None) -> bool:
        """Check if a unit is available to a given civilization."""
        pass

    @abstractmethod
    def is_tech_available(self, civ: Union[str, int], tech_id: str, age: Optional[Age] = None) -> bool:
        """Check if a technology is available to a given civilization."""
        pass

    @abstractmethod
    def is_building_available(self, civ: Union[str, int], building_id: str) -> bool:
        """Check if a building is constructible by a given civilization."""
        pass

    @property
    def num_civs(self) -> int:
        return len(self.civilizations)

    def is_civ_supported(self, civ: Union[str, int]) -> bool:
        """Check if civilization is supported in this patch ruleset."""
        if isinstance(civ, int):
            return civ in self.civilizations
        clean = str(civ).strip().lower()
        return clean in self.civ_name_to_id or clean in [c.lower() for c in self.civilizations.values()]


class RulesRegistry:
    """
    Thread-safe registry mapping version identifiers to GameRuleset instances.
    """
    _rulesets: Dict[str, GameRuleset] = {}
    _latest_version: str = "101.103.x"

    @classmethod
    def register(cls, ruleset: GameRuleset, is_latest: bool = False) -> None:
        """Register a versioned ruleset."""
        version_key = ruleset.patch_version.strip().lower()
        cls._rulesets[version_key] = ruleset
        # Also register common normalized aliases
        if version_key.endswith(".x"):
            cls._rulesets[version_key[:-2]] = ruleset
        if is_latest:
            cls._latest_version = version_key

    @classmethod
    def get(cls, patch_version: Optional[str] = "latest") -> GameRuleset:
        """Resolve and retrieve a ruleset by version string or alias."""
        if not cls._rulesets:
            # Lazy import to populate defaults
            from aoe2_coach.rules.patches.patch_101_102 import Patch101_102_Ruleset
            from aoe2_coach.rules.patches.patch_101_103 import Patch101_103_Ruleset
            cls.register(Patch101_102_Ruleset())
            cls.register(Patch101_103_Ruleset(), is_latest=True)

        if not patch_version or patch_version.lower() in ("latest", "default", "current"):
            return cls._rulesets[cls._latest_version]

        clean = patch_version.strip().lower()
        if clean in cls._rulesets:
            return cls._rulesets[clean]

        # Partial matching (e.g., "101.102" matches "101.102.x")
        for k, r in cls._rulesets.items():
            if clean in k or k in clean:
                return r

        # Fallback to latest
        return cls._rulesets[cls._latest_version]

    @classmethod
    def list_supported_versions(cls) -> List[str]:
        """Return unique supported patch version strings."""
        if not cls._rulesets:
            cls.get("latest")
        return sorted(list({r.patch_version for r in cls._rulesets.values()}))

    @classmethod
    def get_latest_version(cls) -> str:
        return cls._latest_version
