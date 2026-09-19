"""
AoE2: Definitive Edition Patch 101.103.x Ruleset.
Inherits from Patch 101.102.x and introduces:
1. Three new civilizations: Jurchens, Khitans, Shu (expanding from 45 to 48 civilizations).
2. Rebalanced base farm gather rates (0.33 r/s from 0.35).
3. Rebalanced high-ground elevation advantage (+20% from +25%).
4. Unique unit statistics, unique technologies, and archetype affinity vectors for the 3 new civs.
"""

from typing import Dict, List, Optional, Set, Any, Union
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.rules.patches.patch_101_102 import Patch101_102_Ruleset
from aoe2_coach.rules.tech_tree import CivInfo


class Patch101_103_Ruleset(Patch101_102_Ruleset):
    """
    Implementation of Patch 101.103.x with 48 civilizations and modified core mechanics.
    """
    patch_version = "101.103.x"
    display_name = "Definitive Edition (Patch 101.103.x - Three Dynasties & Mechanics Rebalance)"

    def __init__(self):
        super().__init__()

        # 1. Register 3 new civilizations (IDs 46, 47, 48)
        new_civs = {
            46: "Jurchens",
            47: "Khitans",
            48: "Shu",
        }
        self._civs.update(new_civs)
        for cid, name in new_civs.items():
            self._civ_name_to_id[name.lower()] = cid

        # 2. Register strategic archetype affinities for feature vectorization
        self._civ_archetypes["jurchens"] = {
            "cavalry": 1.0,
            "archer": 0.3,
            "infantry": 0.5,
            "siege": 0.9,
            "monk": 0.3,
        }
        self._civ_archetypes["khitans"] = {
            "cavalry": 0.9,
            "archer": 1.0,
            "infantry": 0.3,
            "siege": 0.5,
            "monk": 0.4,
        }
        self._civ_archetypes["shu"] = {
            "cavalry": 0.4,
            "archer": 0.9,
            "infantry": 1.0,
            "siege": 0.6,
            "monk": 0.5,
        }

        # 3. Register CivInfo definitions in civ database
        self._civ_db["jurchens"] = CivInfo(
            id=46,
            name="Jurchens",
            architecture="East Asian",
            unique_units=["iron_pagoda", "elite_iron_pagoda"],
            castle_unique_tech="heavy_brigandine",
            imperial_unique_tech="iron_cavalry",
            civ_bonuses=[
                "Stables cost -50 wood",
                "Siege Workshop units gain +10% HP",
                "Shepherds work 15% faster",
                "Cavalry armor upgrades provide +1 additional melee armor",
            ],
            team_bonus="Siege Workshops work 15% faster",
            disabled_units={"arbalester", "camel_rider", "heavy_camel_rider", "bombard_cannon"},
            disabled_techs={"ring_archer_armor", "thumb_ring"},
        )

        self._civ_db["khitans"] = CivInfo(
            id=47,
            name="Khitans",
            architecture="East Asian",
            unique_units=["ordo_cavalry", "elite_ordo_cavalry"],
            castle_unique_tech="felt_armor",
            imperial_unique_tech="nomadic_feud",
            civ_bonuses=[
                "Cavalry Archers cost -15% food and wood",
                "Bloodlines is free upon reaching Feudal Age",
                "Mounted units have +1 line of sight",
                "Steppe Lancers attack 15% faster",
            ],
            team_bonus="Cavalry Archers created 20% faster",
            disabled_units={"paladin", "arbalester", "hand_cannoneer", "siege_onager"},
            disabled_techs={"plate_mail_armor", "ring_archer_armor"},
        )

        self._civ_db["shu"] = CivInfo(
            id=48,
            name="Shu",
            architecture="East Asian",
            unique_units=["zhuge_vanguard", "elite_zhuge_vanguard"],
            castle_unique_tech="eight_formations",
            imperial_unique_tech="shu_repeater",
            civ_bonuses=[
                "Archery Range units train 20% faster",
                "Blacksmith technologies research instantly",
                "Barracks units cost -15% gold",
                "Crossbow line gains +1 pierce armor in Imperial Age",
            ],
            team_bonus="Foot archers +1 attack vs spearmen",
            disabled_units={"paladin", "camel_rider", "heavy_camel_rider", "hussar", "siege_onager"},
            disabled_techs={"plate_barding_armor", "parthian_tactics"},
        )

        # 4. Modified Core Mechanics
        # Farm gather rate rebalance: 0.33 (from 0.35)
        self._gather_rates["food_farm"] = 0.33
        # Elevation high ground advantage: +20% (from +25%)
        self._elevation_advantage = 0.20
