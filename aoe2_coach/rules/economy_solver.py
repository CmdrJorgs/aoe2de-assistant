"""
AoE2: Definitive Edition Real-Time Villager Production-Balance & Macro Optimizer.

Solves continuous economic production equations, calculates exact gather rates
with tech/civ upgrades, accounts for farm reseeding wood tax, detects stockpile floating,
and outputs optimal villager rebalancing plans.
"""

import math
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field
from aoe2_coach.schemas.match import VillagerAllocation, ResourceStockpile
from aoe2_coach.schemas.game_constants import BASE_GATHER_RATES, Age
from aoe2_coach.rules.units import get_unit_stats, UNITS_DATABASE, ResourceCost
from aoe2_coach.rules.tech_tree import get_civ_info


class GatherRates(BaseModel):
    food_farm: float = 0.35
    food_berries: float = 0.31
    food_sheep: float = 0.33
    food_hunt: float = 0.41
    wood: float = 0.39
    gold: float = 0.38
    stone: float = 0.36


class ResourceRates(BaseModel):
    food_per_sec: float = 0.0
    wood_per_sec: float = 0.0
    gold_per_sec: float = 0.0
    stone_per_sec: float = 0.0


class EconomyOptimizationResult(BaseModel):
    current_allocation: VillagerAllocation
    optimal_allocation: VillagerAllocation
    allocation_deltas: Dict[str, int] = Field(default_factory=dict)
    production_demand_rates: ResourceRates
    current_generation_rates: ResourceRates
    net_resource_balance_rates: ResourceRates
    farm_wood_tax_per_sec: float = 0.0
    bottlenecks: List[str] = Field(default_factory=list)
    actionable_rebalance_steps: List[str] = Field(default_factory=list)
    summary: str = ""


class EconomySolver:
    """
    Mathematical economic optimizer for Age of Empires II macro gameplay.
    """

    def __init__(self):
        pass

    def calculate_gather_rates(
        self,
        researched_techs: Optional[List[str]] = None,
        civ: Optional[str] = None,
    ) -> GatherRates:
        """
        Calculate adjusted resource gather rates per second per villager
        accounting for all eco techs and civilization bonuses.
        """
        tech_set = set(t.lower() for t in (researched_techs or []))
        civ_lower = civ.lower() if civ else ""

        rates = GatherRates()

        # 1. Wood Techs
        wood_mult = 1.0
        if "double_bit_axe" in tech_set:
            wood_mult += 0.20
        if "bow_saw" in tech_set:
            wood_mult += 0.20
        if "two_man_saw" in tech_set:
            wood_mult += 0.10
        if civ_lower == "celts":
            wood_mult += 0.15

        rates.wood = round(BASE_GATHER_RATES["wood"] * wood_mult, 3)

        # 2. Farming / Food Techs
        farm_mult = 1.0
        if "wheelbarrow" in tech_set or civ_lower == "vikings":
            farm_mult += 0.10
        if "hand_cart" in tech_set:
            farm_mult += 0.10
        if civ_lower == "slavs":
            farm_mult += 0.10

        rates.food_farm = round(BASE_GATHER_RATES["food_farm"] * farm_mult, 3)

        # Civ Food Gathering Bonuses
        if civ_lower == "franks":
            rates.food_berries = round(BASE_GATHER_RATES["food_berries"] * 1.15, 3)
        if civ_lower == "britons":
            rates.food_sheep = round(BASE_GATHER_RATES["food_sheep"] * 1.25, 3)
        if civ_lower == "mongols":
            rates.food_hunt = round(BASE_GATHER_RATES["food_hunt"] * 1.40, 3)

        # 3. Gold Techs
        gold_mult = 1.0
        if "gold_mining" in tech_set or civ_lower == "malians":
            gold_mult += 0.15
        if "gold_shaft_mining" in tech_set:
            gold_mult += 0.15
        if civ_lower == "turks":
            gold_mult += 0.20

        rates.gold = round(BASE_GATHER_RATES["gold"] * gold_mult, 3)

        # 4. Stone Techs
        stone_mult = 1.0
        if "stone_mining" in tech_set:
            stone_mult += 0.15
        if "stone_shaft_mining" in tech_set:
            stone_mult += 0.15
        if civ_lower == "koreans":
            stone_mult += 0.20

        rates.stone = round(BASE_GATHER_RATES["stone"] * stone_mult, 3)

        # 5. Aztec universal carry capacity bonus (+3 capacity ~ 6% gather rate)
        if civ_lower == "aztecs":
            rates.wood = round(rates.wood * 1.06, 3)
            rates.food_farm = round(rates.food_farm * 1.06, 3)
            rates.gold = round(rates.gold * 1.06, 3)
            rates.stone = round(rates.stone * 1.06, 3)

        return rates

    def calculate_farm_wood_tax(
        self,
        food_gather_rate: float,
        num_farmers: int,
        researched_techs: Optional[List[str]] = None,
        civ: Optional[str] = None,
    ) -> float:
        """
        Calculate the continuous wood drain (wood/sec) required to keep farms reseeded.
        """
        if num_farmers <= 0:
            return 0.0

        tech_set = set(t.lower() for t in (researched_techs or []))
        civ_lower = civ.lower() if civ else ""

        # Farm capacity
        capacity = 175  # Dark/Feudal base
        if "horse_collar" in tech_set or civ_lower == "franks":
            capacity = 250
        if "heavy_plow" in tech_set:
            capacity = 375
        if "crop_rotation" in tech_set:
            capacity = 550
        if civ_lower == "sicilians":
            capacity = int(capacity * 2.0)

        # Time for 1 farm to deplete in seconds
        farm_duration_sec = capacity / max(0.01, food_gather_rate)
        # Reseed cost is 60 Wood (Teutons farms cost 36 Wood)
        farm_wood_cost = 36 if civ_lower == "teutons" else 60

        wood_tax_per_sec = (farm_wood_cost / max(1.0, farm_duration_sec)) * num_farmers
        return round(wood_tax_per_sec, 3)

    def solve_economy_balance(
        self,
        current_vills: VillagerAllocation,
        current_stockpile: ResourceStockpile,
        target_production: Dict[str, int],  # e.g., {"villager": 1, "knight": 2}
        researched_techs: Optional[List[str]] = None,
        civ: Optional[str] = None,
    ) -> EconomyOptimizationResult:
        """
        Solve optimal villager distribution to sustain continuous production targets
        and balance stockpiles.
        """
        gather_rates = self.calculate_gather_rates(researched_techs, civ)
        total_vills = current_vills.total

        # 1. Calculate required consumption rates (resources per second)
        food_drain = 0.0
        wood_drain = 0.0
        gold_drain = 0.0
        stone_drain = 0.0

        for unit_id, count in target_production.items():
            if count <= 0:
                continue
            stats = get_unit_stats(unit_id)
            if not stats:
                continue
            
            # Rate = (Cost / TrainTime) * Count
            train_time = max(1.0, stats.train_time_sec)
            food_drain += (stats.cost.food / train_time) * count
            wood_drain += (stats.cost.wood / train_time) * count
            gold_drain += (stats.cost.gold / train_time) * count
            stone_drain += (stats.cost.stone / train_time) * count

        # 2. Compute minimum villagers needed for food, gold, stone
        vills_food_needed = math.ceil(food_drain / max(0.01, gather_rates.food_farm))
        vills_gold_needed = math.ceil(gold_drain / max(0.01, gather_rates.gold))
        vills_stone_needed = math.ceil(stone_drain / max(0.01, gather_rates.stone))

        # Farm wood tax
        farm_wood_tax = self.calculate_farm_wood_tax(
            gather_rates.food_farm,
            vills_food_needed,
            researched_techs,
            civ,
        )
        total_wood_drain = wood_drain + farm_wood_tax
        vills_wood_needed = math.ceil(total_wood_drain / max(0.01, gather_rates.wood))

        # Sum of dedicated required vills
        req_total = vills_food_needed + vills_wood_needed + vills_gold_needed + vills_stone_needed

        # 3. Distribute available total villagers proportionally if total differs
        if total_vills <= 0:
            total_vills = req_total

        if req_total > 0:
            scale = total_vills / req_total
            opt_food = max(1 if food_drain > 0 else 0, round(vills_food_needed * scale))
            opt_wood = max(1 if total_wood_drain > 0 else 0, round(vills_wood_needed * scale))
            opt_gold = max(1 if gold_drain > 0 else 0, round(vills_gold_needed * scale))
            opt_stone = max(1 if stone_drain > 0 else 0, round(vills_stone_needed * scale))
        else:
            # Default balanced eco if no production queued
            opt_food = int(total_vills * 0.45)
            opt_wood = int(total_vills * 0.35)
            opt_gold = int(total_vills * 0.20)
            opt_stone = 0

        # Adjust sum to exactly match total_vills
        diff = total_vills - (opt_food + opt_wood + opt_gold + opt_stone)
        opt_wood += diff  # excess or deficit default absorbed by wood

        optimal_alloc = VillagerAllocation(
            total=total_vills,
            food=max(0, opt_food),
            wood=max(0, opt_wood),
            gold=max(0, opt_gold),
            stone=max(0, opt_stone),
            idle_rate=0.0,
        )

        # 4. Deltas (Target - Current)
        deltas = {
            "food": optimal_alloc.food - current_vills.food,
            "wood": optimal_alloc.wood - current_vills.wood,
            "gold": optimal_alloc.gold - current_vills.gold,
            "stone": optimal_alloc.stone - current_vills.stone,
        }

        # 5. Current Generation Rates
        curr_gen_f = round(current_vills.food * gather_rates.food_farm, 2)
        curr_gen_w = round(current_vills.wood * gather_rates.wood, 2)
        curr_gen_g = round(current_vills.gold * gather_rates.gold, 2)
        curr_gen_s = round(current_vills.stone * gather_rates.stone, 2)

        # Net balance rates
        net_f = round(curr_gen_f - food_drain, 2)
        net_w = round(curr_gen_w - total_wood_drain, 2)
        net_g = round(curr_gen_g - gold_drain, 2)
        net_s = round(curr_gen_s - stone_drain, 2)

        # 6. Bottleneck Detection & Stockpile Evaluation
        bottlenecks: List[str] = []
        actionable_steps: List[str] = []

        # Floating wood / gold / food
        if current_stockpile.wood >= 600 and current_stockpile.food < 150:
            bottlenecks.append(f"Floating high wood ({current_stockpile.wood}) while starving on food ({current_stockpile.food}).")
            actionable_steps.append(f"Immediately send {abs(min(-4, deltas['wood']))} woodchoppers to build Farms.")
        elif current_stockpile.wood >= 600 and current_stockpile.gold < 150 and gold_drain > 0:
            bottlenecks.append(f"Floating excess wood ({current_stockpile.wood}) while low on gold ({current_stockpile.gold}).")
            actionable_steps.append(f"Move {abs(min(-4, deltas['wood']))} woodchoppers directly to Mining Camps for Gold.")

        if current_vills.food < vills_food_needed:
            bottlenecks.append(f"Food income ({curr_gen_f}/s) cannot sustain continuous production ({round(food_drain, 2)}/s).")
            if deltas["food"] > 0:
                actionable_steps.append(f"Add {deltas['food']} more villagers to Farms/Food.")

        if current_vills.gold < vills_gold_needed and gold_drain > 0:
            bottlenecks.append(f"Gold income ({curr_gen_g}/s) is below required target ({round(gold_drain, 2)}/s).")
            if deltas["gold"] > 0:
                actionable_steps.append(f"Assign {deltas['gold']} additional villagers to Gold.")

        if current_stockpile.food >= 1200 and current_stockpile.wood < 100:
            bottlenecks.append("Extreme food surplus with wood starvation. Farm reseeding will fail soon.")
            actionable_steps.append("Transfer 6 farmers to Wood.")

        # Formulate concise summary
        prod_names = ", ".join([f"{c}x {u.replace('_', ' ').title()}" for u, c in target_production.items() if c > 0]) or "Balanced Growth"
        summary = (
            f"To sustain [{prod_names}], target allocation is: "
            f"{optimal_alloc.food} Food, {optimal_alloc.wood} Wood, {optimal_alloc.gold} Gold, {optimal_alloc.stone} Stone."
        )

        return EconomyOptimizationResult(
            current_allocation=current_vills,
            optimal_allocation=optimal_alloc,
            allocation_deltas=deltas,
            production_demand_rates=ResourceRates(
                food_per_sec=round(food_drain, 2),
                wood_per_sec=round(total_wood_drain, 2),
                gold_per_sec=round(gold_drain, 2),
                stone_per_sec=round(stone_drain, 2),
            ),
            current_generation_rates=ResourceRates(
                food_per_sec=curr_gen_f,
                wood_per_sec=curr_gen_w,
                gold_per_sec=curr_gen_g,
                stone_per_sec=curr_gen_s,
            ),
            net_resource_balance_rates=ResourceRates(
                food_per_sec=net_f,
                wood_per_sec=net_w,
                gold_per_sec=net_g,
                stone_per_sec=net_s,
            ),
            farm_wood_tax_per_sec=farm_wood_tax,
            bottlenecks=bottlenecks,
            actionable_rebalance_steps=actionable_steps,
            summary=summary,
        )
