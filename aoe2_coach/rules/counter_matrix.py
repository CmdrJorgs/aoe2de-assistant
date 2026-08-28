"""
AoE2: Definitive Edition Dynamic Tactical Counter Matrix & Composition Recommender.

Analyzes sighted enemy forces, identifies threat archetypes and armor vulnerabilities,
filters player civ tech tree restrictions, and ranks optimal military counter responses.
"""

from typing import Dict, List, Optional, Tuple, Set, Union
from pydantic import BaseModel, Field
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.rules.armor_classes import ArmorClass
from aoe2_coach.rules.units import UnitStats, get_unit_stats, UNITS_DATABASE
from aoe2_coach.rules.tech_tree import is_unit_available, get_civ_info
from aoe2_coach.rules.damage_calculator import simulate_duel, calculate_damage_breakdown


class ThreatAnalysis(BaseModel):
    primary_threat_archetype: str  # e.g., "heavy_infantry", "heavy_cavalry", "mass_archers", "siege_push"
    detected_armor_classes: List[str] = Field(default_factory=list)
    dominant_enemy_unit: str = "none"
    total_enemy_count: int = 0
    threat_level: str = "medium"  # "low", "medium", "high", "critical"
    tactical_warning: str = ""


class CounterOption(BaseModel):
    unit_id: str
    unit_name: str
    counter_type: str  # "hard_counter", "soft_counter", "power_composition"
    effectiveness_score: float = 1.0  # 1.0 to 10.0
    production_building: str
    key_technologies: List[str] = Field(default_factory=list)
    tactical_rationale: str
    civ_synergy_note: str = ""


class CounterMatrixResult(BaseModel):
    threat_analysis: ThreatAnalysis
    recommended_counters: List[CounterOption] = Field(default_factory=list)
    primary_unit_recommendation: str
    secondary_support_unit: Optional[str] = None
    production_building_target: str
    tactical_summary: str


class CounterMatrixEngine:
    """
    Tactical decision engine matching enemy compositions to player's optimal civilizational response.
    """

    def __init__(self):
        pass

    def analyze_threat(
        self,
        enemy_units: Dict[str, int],
        enemy_civ: Optional[str] = None,
        enemy_age: Age = Age.CASTLE,
    ) -> ThreatAnalysis:
        """Analyze enemy sighted units and classify the threat archetype."""
        if not enemy_units:
            return ThreatAnalysis(
                primary_threat_archetype="unknown_or_early",
                detected_armor_classes=[],
                dominant_enemy_unit="none",
                total_enemy_count=0,
                threat_level="low",
                tactical_warning="No enemy military sighted yet. Continue scouting enemy forward bases.",
            )

        total_count = sum(enemy_units.values())
        dominant_unit_id = max(enemy_units.items(), key=lambda kv: kv[1])[0].lower()

        # Classify categories
        category_counts: Dict[str, int] = {"cavalry": 0, "archer": 0, "infantry": 0, "siege": 0, "monk": 0}
        detected_classes: Set[str] = set()

        for u_id, count in enemy_units.items():
            stats = get_unit_stats(u_id)
            if stats:
                category_counts[stats.category] = category_counts.get(stats.category, 0) + count
                for ac in stats.armor_classes:
                    detected_classes.add(ac.value)

        primary_cat = max(category_counts.items(), key=lambda kv: kv[1])[0]

        # Determine archetype & warnings
        tactical_warning = ""
        civ_lower = enemy_civ.lower() if enemy_civ else ""

        if dominant_unit_id in ("knight", "cavalier", "paladin", "camel_rider", "scout_cavalry", "light_cavalry", "hussar", "steppe_lancer", "battle_elephant", "monaspa", "centurion"):
            archetype = "heavy_cavalry" if dominant_unit_id in ("knight", "cavalier", "paladin", "monaspa") else "cavalry_mobility"
            if civ_lower == "franks":
                tactical_warning = "Enemy Franks possess +20% HP heavy cavalry. Avoid small skirmishes without dedicated spear/monk defense."
            elif civ_lower == "magyars":
                tactical_warning = "Enemy Magyars have free melee attack upgrades and cheap cavalry."
        elif dominant_unit_id in ("archer", "crossbowman", "arbalester", "cavalry_archer", "heavy_cavalry_archer", "plumed_archer", "longbowman", "mangudai", "rattan_archer", "composite_bowman"):
            archetype = "mass_archers"
            if civ_lower == "britons":
                tactical_warning = "Enemy Britons have extended range. Do not take fight under choke points without Skirmishers or Siege."
            elif civ_lower == "mongols":
                tactical_warning = "Enemy Mongols fast-firing cavalry archers can kite melee units easily."
        elif dominant_unit_id in ("militiaman", "man_at_arms", "long_swordsman", "two_handed_swordsman", "champion", "berserk", "huskarl", "samurai", "jaguar_warrior", "wode_raider", "ghulam", "obuch"):
            archetype = "heavy_infantry"
            if civ_lower == "goths":
                tactical_warning = "Enemy Goths flood infantry rapidly at discounted costs. Prepare Hand Cannoneers or high-DPS heavy units."
            elif civ_lower == "vikings":
                tactical_warning = "Enemy Vikings infantry has high HP. Watch out for Imperial Age Elite Berserk transition."
        elif dominant_unit_id in ("mangonel", "onager", "scorpion", "battering_ram", "bombard_cannon"):
            archetype = "siege_push"
            tactical_warning = "Enemy is massing forward siege. Use cavalry or high mobility units to flank and snipe engines."
        elif dominant_unit_id in ("monk", "missionary"):
            archetype = "monk_rush"
            tactical_warning = "Enemy has heavy monk presence. Rely on Light Cavalry / Eagles to assassinate monks."
        else:
            archetype = f"{primary_cat}_force"

        threat_level = "high" if total_count >= 8 else ("medium" if total_count >= 3 else "low")

        return ThreatAnalysis(
            primary_threat_archetype=archetype,
            detected_armor_classes=sorted(list(detected_classes)),
            dominant_enemy_unit=dominant_unit_id,
            total_enemy_count=total_count,
            threat_level=threat_level,
            tactical_warning=tactical_warning,
        )

    def recommend_counters(
        self,
        player_civ: Union[str, int],
        player_age: Age,
        enemy_units: Dict[str, int],
        enemy_civ: Optional[str] = None,
        player_current_army: Optional[Dict[str, int]] = None,
    ) -> CounterMatrixResult:
        """
        Generate ranked counter options for player's civ against observed enemy units.
        """
        threat = self.analyze_threat(enemy_units, enemy_civ, enemy_age=player_age)
        civ_info = get_civ_info(player_civ)
        civ_name = civ_info.name if civ_info else str(player_civ)

        # Get dominant enemy stats
        enemy_stat = get_unit_stats(threat.dominant_enemy_unit) or get_unit_stats("knight")

        # Candidate units to evaluate from player's tech tree
        candidate_options: List[CounterOption] = []

        # 1. Evaluate all available units for player civ up to player's age
        for u_id, u_stat in UNITS_DATABASE.items():
            if u_stat.age > player_age:
                continue
            if not is_unit_available(player_civ, u_id):
                continue
            if u_stat.is_unique and u_stat.civ and u_stat.civ.lower() != civ_name.lower():
                continue
            if u_stat.category == "economy" or u_id in ("villager", "trade_cart", "fishing_ship"):
                continue

            # Simulate duel vs dominant enemy
            duel = simulate_duel(
                u_stat,
                enemy_stat,
                unit1_civ=civ_name,
                unit2_civ=enemy_civ,
            )

            # Determine key technologies
            key_techs = []
            if u_stat.category == "cavalry":
                key_techs.extend(["scale_barding_armor", "bloodlines"] if player_age == Age.FEUDAL else ["chain_barding_armor", "husbandry", "bloodlines"])
            elif u_stat.category == "archer":
                key_techs.extend(["fletching", "padded_archer_armor"] if player_age == Age.FEUDAL else ["bodkin_arrow", "leather_archer_armor", "ballistics"])
            elif u_stat.category == "infantry":
                key_techs.extend(["scale_mail_armor", "forging"] if player_age == Age.FEUDAL else ["chain_mail_armor", "iron_casting", "squires"])

            # Check civ synergies
            civ_synergy = ""
            if civ_name.lower() == "franks" and u_stat.category == "cavalry":
                civ_synergy = "Franks grant +20% HP to cavalry."
            elif civ_name.lower() == "britons" and u_stat.category == "archer":
                civ_synergy = "Britons grant extra range to foot archers."
            elif civ_name.lower() == "byzantines" and u_id in ("spearman", "pikeman", "skirmisher", "elite_skirmisher", "camel_rider"):
                civ_synergy = "Byzantines reduce counter unit cost by 25%."
            elif civ_name.lower() == "goths" and u_stat.category == "infantry":
                civ_synergy = "Goths produce cheaper infantry 20% faster."
            elif civ_name.lower() == "japanese" and u_stat.category == "infantry":
                civ_synergy = "Japanese infantry attack 33% faster."
            elif civ_name.lower() == "hindustanis" and "camel" in u_id:
                civ_synergy = "Hindustanis camels attack 20% faster."

            # Hard vs soft counter scoring
            if duel.is_hard_counter:
                counter_type = "hard_counter"
                score = 8.5 + min(1.5, duel.cost_efficiency * 0.2)
            elif duel.is_soft_counter:
                counter_type = "soft_counter"
                score = 6.5 + min(1.5, duel.cost_efficiency * 0.2)
            elif duel.winner_id == u_stat.id:
                counter_type = "power_composition"
                score = 5.5
            else:
                # Still check if unit has high situational utility (e.g. Mangonel vs Crossbows or Monks vs Knights)
                if enemy_stat.category == "archer" and u_id in ("mangonel", "onager", "skirmisher", "elite_skirmisher"):
                    counter_type = "hard_counter"
                    score = 8.0
                elif enemy_stat.category == "cavalry" and u_id in ("spearman", "pikeman", "halberdier", "monk", "camel_rider", "heavy_camel_rider"):
                    counter_type = "hard_counter"
                    score = 8.8
                elif enemy_stat.category == "infantry" and u_id in ("hand_cannoneer", "crossbowman", "arbalester", "knight", "cavalier", "scorpion"):
                    counter_type = "soft_counter"
                    score = 7.2
                else:
                    continue

            # Boost score for unique units of player civ
            if u_stat.is_unique:
                score += 0.5

            candidate_options.append(
                CounterOption(
                    unit_id=u_stat.id,
                    unit_name=u_stat.name,
                    counter_type=counter_type,
                    effectiveness_score=round(score, 1),
                    production_building=u_stat.train_building,
                    key_technologies=key_techs,
                    tactical_rationale=duel.explanation or f"{u_stat.name} counters {enemy_stat.name}.",
                    civ_synergy_note=civ_synergy,
                )
            )

        # Sort candidate options by effectiveness score descending
        candidate_options.sort(key=lambda o: o.effectiveness_score, reverse=True)

        # Select top recommendations
        primary = candidate_options[0].unit_name if candidate_options else "Crossbowman"
        secondary = candidate_options[1].unit_name if len(candidate_options) > 1 else None
        prod_building = candidate_options[0].production_building if candidate_options else "archery_range"

        summary = f"Identified enemy {threat.primary_threat_archetype.replace('_', ' ')} centered around {enemy_stat.name}. Recommended response: Mass {primary} supported by {secondary or 'siege engines'} from {prod_building.replace('_', ' ')}."

        return CounterMatrixResult(
            threat_analysis=threat,
            recommended_counters=candidate_options[:5],
            primary_unit_recommendation=primary,
            secondary_support_unit=secondary,
            production_building_target=prod_building,
            tactical_summary=summary,
        )
