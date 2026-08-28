"""
AoE2: Definitive Edition Armor Classes and Class Hierarchy.

In the AoE2 game engine, all units and buildings have one or more armor classes.
Attacks have base damage in MELEE or PIERCE, plus bonus damage against specific armor classes.
"""

from enum import Enum, unique
from typing import Dict


@unique
class ArmorClass(str, Enum):
    MELEE = "melee"
    PIERCE = "pierce"
    INFANTRY = "infantry"
    SPEARMAN = "spearman"
    CAVALRY = "cavalry"
    ARCHER = "archer"
    CAVALRY_ARCHER = "cavalry_archer"
    SIEGE = "siege"
    RAM = "ram"
    ELEPHANT = "elephant"
    CAMEL = "camel"
    EAGLE_WARRIOR = "eagle_warrior"
    CONDOTTIERO = "condottiero"
    GUNPOWDER = "gunpowder"
    BUILDING = "building"
    STANDARD_BUILDING = "standard_building"
    WALL_GATE = "wall_gate"
    CASTLE = "castle"
    SHIP = "ship"
    FISHING_SHIP = "fishing_ship"
    UNIQUE_UNIT = "unique_unit"
    MONK = "monk"

    @property
    def display_name(self) -> str:
        return self.value.replace("_", " ").title()


# Numerical internal IDs from AoE2 engine
ARMOR_CLASS_ENGINE_IDS: Dict[ArmorClass, int] = {
    ArmorClass.MELEE: 0,
    ArmorClass.INFANTRY: 1,
    ArmorClass.SPEARMAN: 2,
    ArmorClass.PIERCE: 3,
    ArmorClass.CAVALRY: 8,
    ArmorClass.GUNPOWDER: 11,
    ArmorClass.SIEGE: 13,
    ArmorClass.ARCHER: 15,
    ArmorClass.UNIQUE_UNIT: 19,
    ArmorClass.RAM: 20,
    ArmorClass.BUILDING: 21,
    ArmorClass.SHIP: 22,
    ArmorClass.EAGLE_WARRIOR: 25,
    ArmorClass.CASTLE: 26,
    ArmorClass.CAVALRY_ARCHER: 28,
    ArmorClass.MONK: 29,
    ArmorClass.CAMEL: 30,
    ArmorClass.FISHING_SHIP: 31,
    ArmorClass.CONDOTTIERO: 33,
    ArmorClass.STANDARD_BUILDING: 34,
    ArmorClass.WALL_GATE: 35,
    ArmorClass.ELEPHANT: 19,
}
