"""
AoE2 Coach Domain Knowledge & Rules Engine.

Includes:
- Armor Classes & Engine IDs
- Complete Unit Statistics & Catalog
- 45+ Civilization Tech Trees & Bonuses
- Exact Damage Calculation & Combat Simulation
- Tactical Counter Matrix & Threat Analyzer
- Real-Time Villager Production-Balance Economy Solver
"""

from aoe2_coach.rules.armor_classes import (
    ArmorClass,
    ARMOR_CLASS_ENGINE_IDS,
)
from aoe2_coach.rules.units import (
    ResourceCost,
    UnitStats,
    UNITS_DATABASE,
    get_unit_stats,
)
from aoe2_coach.rules.tech_tree import (
    Tech,
    CivInfo,
    TECHS_DATABASE,
    CIVILIZATIONS_DATABASE,
    get_civ_info,
    is_unit_available,
    is_tech_available,
    is_building_available,
    get_all_civs,
)
from aoe2_coach.rules.damage_calculator import (
    DamageBreakdown,
    CombatOutcome,
    DuelSimulationResult,
    calculate_damage_breakdown,
    simulate_duel,
    apply_tech_and_civ_modifiers,
)
from aoe2_coach.rules.counter_matrix import (
    ThreatAnalysis,
    CounterOption,
    CounterMatrixResult,
    CounterMatrixEngine,
)
from aoe2_coach.rules.economy_solver import (
    GatherRates,
    ResourceRates,
    EconomyOptimizationResult,
    EconomySolver,
)

__all__ = [
    "ArmorClass",
    "ARMOR_CLASS_ENGINE_IDS",
    "ResourceCost",
    "UnitStats",
    "UNITS_DATABASE",
    "get_unit_stats",
    "Tech",
    "CivInfo",
    "TECHS_DATABASE",
    "CIVILIZATIONS_DATABASE",
    "get_civ_info",
    "is_unit_available",
    "is_tech_available",
    "is_building_available",
    "get_all_civs",
    "DamageBreakdown",
    "CombatOutcome",
    "DuelSimulationResult",
    "calculate_damage_breakdown",
    "simulate_duel",
    "apply_tech_and_civ_modifiers",
    "ThreatAnalysis",
    "CounterOption",
    "CounterMatrixResult",
    "CounterMatrixEngine",
    "GatherRates",
    "ResourceRates",
    "EconomyOptimizationResult",
    "EconomySolver",
]
