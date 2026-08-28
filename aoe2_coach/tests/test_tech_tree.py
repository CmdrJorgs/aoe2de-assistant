"""
Tests for AoE2 Tech Tree, 45 Civilizations, Unique Units, and Availability Guardrails.
"""

import pytest
from aoe2_coach.schemas.game_constants import Age, CIVILIZATIONS
from aoe2_coach.rules.tech_tree import (
    get_civ_info,
    is_unit_available,
    is_tech_available,
    is_building_available,
    get_all_civs,
    CIVILIZATIONS_DATABASE,
)
from aoe2_coach.rules.units import UNITS_DATABASE


def test_all_45_civilizations_registered():
    all_civs = get_all_civs()
    assert len(all_civs) == 45
    for cid, cname in CIVILIZATIONS.items():
        info = get_civ_info(cid)
        assert info is not None, f"Civ ID {cid} ({cname}) missing in database"
        assert info.name.lower() == cname.lower()
        assert len(info.civ_bonuses) > 0
        assert len(info.unique_units) > 0


def test_mesoamerican_cavalry_restrictions():
    meso_civs = ["aztecs", "mayans", "incas"]
    for civ in meso_civs:
        assert not is_building_available(civ, "stable")
        assert not is_unit_available(civ, "scout_cavalry")
        assert not is_unit_available(civ, "knight")
        assert not is_unit_available(civ, "cavalier")
        assert not is_unit_available(civ, "paladin")
        assert not is_unit_available(civ, "camel_rider")
        assert is_unit_available(civ, "eagle_scout")
        assert is_unit_available(civ, "eagle_warrior")


def test_goth_building_and_tech_restrictions():
    assert not is_building_available("goths", "stone_wall")
    assert not is_building_available("goths", "guard_tower")
    assert not is_unit_available("goths", "paladin")
    assert not is_tech_available("goths", "plate_barding_armor")
    assert is_unit_available("goths", "huskarl")


def test_franks_civ_specifications():
    franks = get_civ_info("franks")
    assert franks is not None
    assert "throwing_axeman" in franks.unique_units
    assert not is_unit_available("franks", "arbalester")
    assert not is_tech_available("franks", "bracer")
    assert is_unit_available("franks", "paladin")
    assert is_unit_available("franks", "knight")


def test_britons_specifications():
    britons = get_civ_info("britons")
    assert britons is not None
    assert "longbowman" in britons.unique_units
    assert not is_unit_available("britons", "paladin")
    assert not is_tech_available("britons", "thumb_ring")
    assert not is_tech_available("britons", "bloodlines")
    assert is_unit_available("britons", "arbalester")
