"""
AoE2: Definitive Edition Armor Class & Damage Formula Engine.

Implements exact deterministic damage calculation, armor class resolution,
blacksmith upgrades, elevation modifiers, civ bonuses, and 1v1 / army combat simulations.
"""

import math
from typing import Dict, List, Optional, Tuple, Set
from pydantic import BaseModel, Field
from aoe2_coach.rules.armor_classes import ArmorClass
from aoe2_coach.rules.units import UnitStats, get_unit_stats, ResourceCost


class DamageBreakdown(BaseModel):
    primary_damage: float = 0.0
    bonus_damage: float = 0.0
    bonus_details: Dict[str, float] = Field(default_factory=dict)
    elevation_multiplier: float = 1.0
    net_damage_per_hit: float = 1.0
    hits_to_kill: int = 1
    time_to_kill_sec: float = 1.0
    dps: float = 1.0


class CombatOutcome(BaseModel):
    attacker_name: str
    defender_name: str
    damage_per_hit: float
    hits_to_kill: int
    time_to_kill_sec: float
    dps: float


class DuelSimulationResult(BaseModel):
    winner_id: str
    winner_name: str
    loser_id: str
    loser_name: str
    winner_remaining_hp: float
    winner_hp_percent: float
    unit1_outcome: CombatOutcome
    unit2_outcome: CombatOutcome
    cost_efficiency: float = 1.0  # > 1.0 means unit1 trades cost-effectively against unit2
    is_hard_counter: bool = False
    is_soft_counter: bool = False
    explanation: str = ""


# Blacksmith / Tech Stat Buff Rules
TECH_STAT_MODIFIERS: Dict[str, Dict[str, any]] = {
    # Melee attack
    "forging": {"melee_attack": 1},
    "iron_casting": {"melee_attack": 1},
    "blast_furnace": {"melee_attack": 2},
    # Archer attack & range
    "fletching": {"pierce_attack": 1, "range": 1.0},
    "bodkin_arrow": {"pierce_attack": 1, "range": 1.0},
    "bracer": {"pierce_attack": 1, "range": 1.0},
    # Infantry armor
    "scale_mail_armor": {"infantry_melee_armor": 1, "infantry_pierce_armor": 1},
    "chain_mail_armor": {"infantry_melee_armor": 1, "infantry_pierce_armor": 1},
    "plate_mail_armor": {"infantry_melee_armor": 1, "infantry_pierce_armor": 2},
    # Cavalry armor
    "scale_barding_armor": {"cavalry_melee_armor": 1, "cavalry_pierce_armor": 1},
    "chain_barding_armor": {"cavalry_melee_armor": 1, "cavalry_pierce_armor": 1},
    "plate_barding_armor": {"cavalry_melee_armor": 1, "cavalry_pierce_armor": 2},
    # Archer armor
    "padded_archer_armor": {"archer_melee_armor": 1, "archer_pierce_armor": 1},
    "leather_archer_armor": {"archer_melee_armor": 1, "archer_pierce_armor": 1},
    "ring_archer_armor": {"archer_melee_armor": 1, "archer_pierce_armor": 2},
    # General
    "bloodlines": {"mounted_hp": 20},
    "husbandry": {"cavalry_speed_multiplier": 1.10},
    "squires": {"infantry_speed_multiplier": 1.10},
    "thumb_ring": {"archer_accuracy": 1.0, "archer_reload_multiplier": 0.85},
    "parthian_tactics": {"cavalry_archer_melee_armor": 1, "cavalry_archer_pierce_armor": 2, "cavalry_archer_spearman_bonus": 4},
}


def apply_tech_and_civ_modifiers(
    unit: UnitStats,
    techs: Optional[List[str]] = None,
    civ: Optional[str] = None,
) -> UnitStats:
    """Create an adjusted clone of UnitStats with researched techs and civ bonuses applied."""
    u = unit.model_copy(deep=True)
    tech_set = set(t.lower() for t in (techs or []))
    civ_name = civ.lower() if civ else (u.civ.lower() if u.civ else None)

    # 1. Apply Blacksmith & General Technologies
    for tech_id in tech_set:
        mods = TECH_STAT_MODIFIERS.get(tech_id, {})
        
        # Attack buffs
        if "melee_attack" in mods and u.attack_type == ArmorClass.MELEE:
            u.base_attack += mods["melee_attack"]
        if "pierce_attack" in mods and u.attack_type == ArmorClass.PIERCE:
            u.base_attack += mods["pierce_attack"]
        if "range" in mods and u.category in ("archer", "navy", "siege") and u.range > 0:
            u.range += mods["range"]

        # Armor buffs
        if u.category == "infantry":
            u.base_armor_melee += mods.get("infantry_melee_armor", 0)
            u.base_armor_pierce += mods.get("infantry_pierce_armor", 0)
        elif u.category == "cavalry":
            u.base_armor_melee += mods.get("cavalry_melee_armor", 0)
            u.base_armor_pierce += mods.get("cavalry_pierce_armor", 0)
        elif u.category == "archer":
            u.base_armor_melee += mods.get("archer_melee_armor", 0)
            u.base_armor_pierce += mods.get("archer_pierce_armor", 0)

        # Mounted HP (Bloodlines)
        if "mounted_hp" in mods and (u.category == "cavalry" or ArmorClass.CAVALRY in u.armor_classes or ArmorClass.CAMEL in u.armor_classes):
            u.hp += mods["mounted_hp"]

        # Parthian tactics
        if "cavalry_archer_spearman_bonus" in mods and ArmorClass.CAVALRY_ARCHER in u.armor_classes:
            u.base_armor_melee += mods.get("cavalry_archer_melee_armor", 0)
            u.base_armor_pierce += mods.get("cavalry_archer_pierce_armor", 0)
            u.attack_bonuses[ArmorClass.SPEARMAN] = u.attack_bonuses.get(ArmorClass.SPEARMAN, 0) + mods["cavalry_archer_spearman_bonus"]

    # 2. Apply Civilization Bonuses
    if civ_name == "franks":
        if u.category == "cavalry":
            u.hp = int(u.hp * 1.20)  # +20% HP
    elif civ_name == "britons":
        if u.category == "archer" and u.id not in ("skirmisher", "elite_skirmisher", "imperial_skirmisher"):
            if u.age >= 3:
                u.range += 1.0
            if u.age >= 4:
                u.range += 1.0
    elif civ_name == "mongols":
        if u.id in ("scout_cavalry", "light_cavalry", "hussar", "steppe_lancer", "elite_steppe_lancer"):
            u.hp = int(u.hp * 1.30)
        if u.id in ("cavalry_archer", "heavy_cavalry_archer", "mangudai", "elite_mangudai"):
            u.reload_time *= 0.75  # 25% faster firing
    elif civ_name == "vikings":
        if u.category == "infantry":
            u.hp = int(u.hp * 1.20)
    elif civ_name == "japanese":
        if u.category == "infantry":
            u.reload_time *= 0.67  # 33% faster attack
    elif civ_name == "turks":
        if ArmorClass.GUNPOWDER in u.armor_classes:
            u.hp = int(u.hp * 1.25)
    elif civ_name == "ethiopians":
        if u.category == "archer":
            u.reload_time *= 0.82  # 18% faster firing

    return u


def calculate_damage_breakdown(
    attacker: UnitStats,
    defender: UnitStats,
    elevation: str = "flat",  # "high", "low", "flat"
    attacker_civ: Optional[str] = None,
    defender_civ: Optional[str] = None,
) -> DamageBreakdown:
    """
    Calculate exact damage per strike from attacker to defender according to AoE2 engine rules.
    """
    # 1. Primary damage (Melee or Pierce)
    if attacker.attack_type == ArmorClass.PIERCE:
        primary_armor = defender.base_armor_pierce
    else:
        primary_armor = defender.base_armor_melee

    primary_damage = max(0, attacker.base_attack - primary_armor)

    # 2. Bonus Class Damage
    bonus_damage = 0.0
    bonus_details: Dict[str, float] = {}

    for armor_class, bonus_atk in attacker.attack_bonuses.items():
        if armor_class in defender.armor_classes:
            defender_class_armor = defender.armor_classes[armor_class]
            class_dmg = max(0, bonus_atk - defender_class_armor)
            if class_dmg > 0:
                # Civ special: Sicilians reduce incoming bonus damage by 33%
                if defender_civ and defender_civ.lower() == "sicilians":
                    class_dmg = round(class_dmg * 0.67, 2)
                bonus_damage += class_dmg
                bonus_details[armor_class.value] = class_dmg

    raw_damage = primary_damage + bonus_damage

    # AoE2 Rule: minimum 1 damage per successful hit
    base_net = max(1.0, float(raw_damage))

    # 3. Elevation Multiplier
    elevation_mult = 1.0
    if elevation == "high":
        # Attacker is on hill
        if attacker_civ and attacker_civ.lower() == "tatars":
            elevation_mult = 1.50  # Tatars +50% hill damage
        else:
            elevation_mult = 1.25  # Standard +25%
    elif elevation == "low":
        # Defender is on hill
        if defender_civ and defender_civ.lower() == "georgians":
            elevation_mult = 0.85  # Georgians take less damage
        else:
            elevation_mult = 0.75  # Standard -25%

    net_damage_per_hit = max(1.0, base_net * elevation_mult)
    effective_damage_per_shot = net_damage_per_hit * attacker.accuracy

    # 4. Hits and Time to Kill
    hits_to_kill = math.ceil(defender.hp / max(1.0, net_damage_per_hit))
    effective_shots = math.ceil(defender.hp / max(1.0, effective_damage_per_shot))
    time_to_kill_sec = round((effective_shots - 1) * attacker.reload_time, 2)
    dps = round(effective_damage_per_shot / attacker.reload_time, 2)

    return DamageBreakdown(
        primary_damage=float(primary_damage),
        bonus_damage=float(bonus_damage),
        bonus_details=bonus_details,
        elevation_multiplier=elevation_mult,
        net_damage_per_hit=round(net_damage_per_hit, 2),
        hits_to_kill=hits_to_kill,
        time_to_kill_sec=time_to_kill_sec,
        dps=dps,
    )


_DUEL_CACHE: Dict[Tuple[str, str, str, str, str, str, str], DuelSimulationResult] = {}


def simulate_duel(
    unit1: UnitStats,
    unit2: UnitStats,
    unit1_techs: Optional[List[str]] = None,
    unit2_techs: Optional[List[str]] = None,
    unit1_civ: Optional[str] = None,
    unit2_civ: Optional[str] = None,
    elevation: str = "flat",
) -> DuelSimulationResult:
    """
    Simulate a deterministic 1v1 duel between two units with given upgrades and civ modifiers.
    """
    cache_key = (
        unit1.id,
        unit2.id,
        ",".join(sorted(unit1_techs or [])),
        ",".join(sorted(unit2_techs or [])),
        (unit1_civ or "").lower(),
        (unit2_civ or "").lower(),
        elevation,
    )
    if cache_key in _DUEL_CACHE:
        return _DUEL_CACHE[cache_key]

    u1 = apply_tech_and_civ_modifiers(unit1, unit1_techs, unit1_civ)
    u2 = apply_tech_and_civ_modifiers(unit2, unit2_techs, unit2_civ)

    outcome_1_on_2 = calculate_damage_breakdown(u1, u2, elevation=elevation, attacker_civ=unit1_civ, defender_civ=unit2_civ)
    outcome_2_on_1 = calculate_damage_breakdown(u2, u1, elevation=elevation, attacker_civ=unit2_civ, defender_civ=unit1_civ)

    ttk_1 = outcome_1_on_2.time_to_kill_sec
    ttk_2 = outcome_2_on_1.time_to_kill_sec

    # Unit with lower TTK wins
    if ttk_1 < ttk_2:
        winner_id = u1.id
        winner_name = u1.name
        loser_id = u2.id
        loser_name = u2.name
        # Winner remaining HP after duel duration
        damage_taken = (ttk_1 / max(0.1, u2.reload_time)) * outcome_2_on_1.net_damage_per_hit
        winner_rem_hp = max(1.0, u1.hp - damage_taken)
        winner_pct = round((winner_rem_hp / u1.hp) * 100.0, 1)
    else:
        winner_id = u2.id
        winner_name = u2.name
        loser_id = u1.id
        loser_name = u1.name
        damage_taken = (ttk_2 / max(0.1, u1.reload_time)) * outcome_1_on_2.net_damage_per_hit
        winner_rem_hp = max(1.0, u2.hp - damage_taken)
        winner_pct = round((winner_rem_hp / u2.hp) * 100.0, 1)

    # Cost-effectiveness evaluation (Resource-adjusted combat trade)
    u1_cost = max(1, u1.cost.total)
    u2_cost = max(1, u2.cost.total)
    cost_ratio = u2_cost / u1_cost
    combat_efficiency = round((ttk_2 / max(0.1, ttk_1)) * cost_ratio, 2)

    # Hard vs Soft counter heuristics
    is_hard_counter = False
    is_soft_counter = False
    explanation_parts = []

    if outcome_1_on_2.bonus_damage > 0:
        bonuses = [f"+{int(v)} vs {k.replace('_', ' ')}" for k, v in outcome_1_on_2.bonus_details.items()]
        explanation_parts.append(f"{u1.name} deals bonus damage ({', '.join(bonuses)}).")

    if winner_id == u1.id and combat_efficiency >= 2.0:
        is_hard_counter = True
        explanation_parts.append(f"Hard counter: {u1.name} defeats {u2.name} in {ttk_1}s with {combat_efficiency}x cost efficiency.")
    elif winner_id == u1.id and combat_efficiency >= 1.2:
        is_soft_counter = True
        explanation_parts.append(f"Soft counter: {u1.name} trades favorably against {u2.name} ({combat_efficiency}x efficiency).")
    elif winner_id == u2.id:
        explanation_parts.append(f"{u2.name} defeats {u1.name} in {ttk_2}s.")

    res = DuelSimulationResult(
        winner_id=winner_id,
        winner_name=winner_name,
        loser_id=loser_id,
        loser_name=loser_name,
        winner_remaining_hp=round(winner_rem_hp, 1),
        winner_hp_percent=winner_pct,
        unit1_outcome=CombatOutcome(
            attacker_name=u1.name,
            defender_name=u2.name,
            damage_per_hit=outcome_1_on_2.net_damage_per_hit,
            hits_to_kill=outcome_1_on_2.hits_to_kill,
            time_to_kill_sec=outcome_1_on_2.time_to_kill_sec,
            dps=outcome_1_on_2.dps,
        ),
        unit2_outcome=CombatOutcome(
            attacker_name=u2.name,
            defender_name=u1.name,
            damage_per_hit=outcome_2_on_1.net_damage_per_hit,
            hits_to_kill=outcome_2_on_1.hits_to_kill,
            time_to_kill_sec=outcome_2_on_1.time_to_kill_sec,
            dps=outcome_2_on_1.dps,
        ),
        cost_efficiency=combat_efficiency,
        is_hard_counter=is_hard_counter,
        is_soft_counter=is_soft_counter,
        explanation=" ".join(explanation_parts),
    )
    _DUEL_CACHE[cache_key] = res
    return res
