"""
Tests for AoE2 Armor Classes, Damage Calculations, Elevation Modifiers, and Combat Duels.
"""

import pytest
from aoe2_coach.rules.armor_classes import ArmorClass
from aoe2_coach.rules.units import get_unit_stats
from aoe2_coach.rules.damage_calculator import (
    calculate_damage_breakdown,
    simulate_duel,
    apply_tech_and_civ_modifiers,
)


def test_base_melee_damage():
    # Militia (4 attack melee, 0 armor) vs Militia (4 attack melee, 0 armor)
    militia = get_unit_stats("militiaman")
    dmg = calculate_damage_breakdown(militia, militia)
    assert dmg.primary_damage == 4.0
    assert dmg.bonus_damage == 0.0
    assert dmg.net_damage_per_hit == 4.0
    assert dmg.hits_to_kill == 10  # 40 HP / 4 dmg = 10 hits


def test_bonus_damage_spearman_vs_knight():
    # Spearman has 3 base attack + 15 bonus vs Cavalry.
    # Knight has 2 base melee armor and 0 Cavalry armor.
    # Primary damage = max(0, 3 - 2) = 1.
    # Bonus damage = max(0, 15 - 0) = 15.
    # Net damage = 1 + 15 = 16.
    spearman = get_unit_stats("spearman")
    knight = get_unit_stats("knight")

    dmg = calculate_damage_breakdown(spearman, knight)
    assert dmg.primary_damage == 1.0
    assert dmg.bonus_damage == 15.0
    assert dmg.net_damage_per_hit == 16.0
    assert dmg.hits_to_kill == 7  # 100 HP / 16 = 6.25 -> 7 hits


def test_bonus_damage_halberdier_vs_paladin():
    # Halberdier: 6 base melee, +32 vs Cavalry.
    # Paladin: 2 melee armor, 0 cavalry armor.
    # Primary = 6 - 2 = 4. Bonus = 32. Net = 36 damage!
    halb = get_unit_stats("halberdier")
    paladin = get_unit_stats("paladin")

    dmg = calculate_damage_breakdown(halb, paladin)
    assert dmg.primary_damage == 4.0
    assert dmg.bonus_damage == 32.0
    assert dmg.net_damage_per_hit == 36.0
    assert dmg.hits_to_kill == 5  # 160 HP / 36 = 4.44 -> 5 hits


def test_skirmisher_vs_crossbowman():
    # Elite Skirmisher (3 pierce, +4 vs Archer). Crossbowman (35 HP, 0/0 armor, Archer class).
    # Net = 3 + 4 = 7 damage.
    skirm = get_unit_stats("elite_skirmisher")
    xbow = get_unit_stats("crossbowman")

    dmg = calculate_damage_breakdown(skirm, xbow)
    assert dmg.primary_damage == 3.0
    assert dmg.bonus_damage == 4.0
    assert dmg.net_damage_per_hit == 7.0
    assert dmg.hits_to_kill == 5  # 35 HP / 7 = 5 hits


def test_hand_cannoneer_vs_infantry():
    # Hand Cannoneer: 17 pierce, +10 vs Infantry.
    # Champion: 70 HP, 1 pierce armor.
    # Primary = 17 - 1 = 16. Bonus = 10. Raw = 26 damage.
    # Hand cannoneer accuracy is 0.75 -> expected average damage = 26 * 0.75 = 19.5
    hc = get_unit_stats("hand_cannoneer")
    champ = get_unit_stats("champion")

    dmg = calculate_damage_breakdown(hc, champ)
    assert dmg.primary_damage == 16.0
    assert dmg.bonus_damage == 10.0
    assert dmg.net_damage_per_hit == 26.0
    assert dmg.dps == round(26.0 * 0.75 / 3.45, 2)  # 5.65


def test_elevation_bonus():
    knight = get_unit_stats("knight")
    dmg_flat = calculate_damage_breakdown(knight, knight, elevation="flat")
    dmg_high = calculate_damage_breakdown(knight, knight, elevation="high")
    dmg_low = calculate_damage_breakdown(knight, knight, elevation="low")

    # Base knight on knight: 10 - 2 = 8.
    assert dmg_flat.net_damage_per_hit == 8.0
    assert dmg_high.net_damage_per_hit == 10.0  # 8 * 1.25
    assert dmg_low.net_damage_per_hit == 6.0   # 8 * 0.75


def test_tatar_hill_bonus():
    knight = get_unit_stats("knight")
    dmg_tatar = calculate_damage_breakdown(knight, knight, elevation="high", attacker_civ="tatars")
    # 8 * 1.50 = 12.0
    assert dmg_tatar.net_damage_per_hit == 12.0


def test_blacksmith_tech_modifiers():
    knight = get_unit_stats("knight")
    upgraded = apply_tech_and_civ_modifiers(
        knight,
        techs=["forging", "iron_casting", "scale_barding_armor", "chain_barding_armor", "bloodlines"],
        civ="franks",
    )
    # Base: 10 attack, 2/2 armor, 100 HP.
    # Techs: +2 attack (12), +2/+2 armor (4/4), Bloodlines (+20 HP -> 120).
    # Franks +20% HP -> 120 * 1.2 = 144 HP.
    assert upgraded.base_attack == 12
    assert upgraded.base_armor_melee == 4
    assert upgraded.base_armor_pierce == 4
    assert upgraded.hp == 144


def test_duel_simulation_hard_counter():
    pikeman = get_unit_stats("pikeman")
    knight = get_unit_stats("knight")

    duel = simulate_duel(pikeman, knight)
    assert duel.is_hard_counter or duel.cost_efficiency >= 1.5
    assert duel.unit1_outcome.damage_per_hit >= 20.0  # 4 base - 2 armor + 22 bonus = 24
