"""
Tests for Real-Time Villager Production-Balance Economy Solver & Gather Rate Equations.
"""

import pytest
from aoe2_coach.schemas.match import VillagerAllocation, ResourceStockpile
from aoe2_coach.rules.economy_solver import EconomySolver, GatherRates


def test_base_gather_rates():
    solver = EconomySolver()
    rates = solver.calculate_gather_rates()
    assert rates.wood == 0.39
    assert rates.food_farm == 0.35
    assert rates.gold == 0.38
    assert rates.stone == 0.36


def test_wood_and_farm_upgrades():
    solver = EconomySolver()
    rates = solver.calculate_gather_rates(
        researched_techs=["double_bit_axe", "bow_saw", "wheelbarrow"]
    )
    # Wood: 0.39 * (1 + 0.20 + 0.20) = 0.39 * 1.40 = 0.546
    assert rates.wood == 0.546
    # Farm: 0.35 * 1.10 = 0.385
    assert rates.food_farm == 0.385


def test_civ_gathering_bonuses():
    solver = EconomySolver()
    celt_rates = solver.calculate_gather_rates(civ="celts")
    assert celt_rates.wood == round(0.39 * 1.15, 3)  # 0.448

    frank_rates = solver.calculate_gather_rates(civ="franks")
    assert frank_rates.food_berries == round(0.31 * 1.15, 3)

    briton_rates = solver.calculate_gather_rates(civ="britons")
    assert briton_rates.food_sheep == round(0.33 * 1.25, 3)

    turk_rates = solver.calculate_gather_rates(civ="turks")
    assert turk_rates.gold == round(0.38 * 1.20, 3)


def test_farm_wood_tax():
    solver = EconomySolver()
    # 20 farmers with base capacity (175 food).
    # Food gather = 0.35 food/s -> Farm lasts 175 / 0.35 = 500s.
    # Wood tax = (60 / 500) * 20 = 2.4 wood/s.
    wood_tax = solver.calculate_farm_wood_tax(
        food_gather_rate=0.35,
        num_farmers=20,
    )
    assert wood_tax == 2.4


def test_continuous_knights_and_villagers_solve():
    solver = EconomySolver()
    # Production: 2 Stables Knights (60F, 75G per 30s each = 4F/s, 5G/s)
    # + 1 TC Villagers (50F per 25s = 2F/s)
    # Total Food drain = 6.0 F/s -> ~18 farmers.
    # Total Gold drain = 5.0 G/s -> ~14 gold miners.
    current_vills = VillagerAllocation(
        total=45,
        food=15,
        wood=22,
        gold=6,
        stone=2,
    )
    stockpile = ResourceStockpile(food=100, wood=750, gold=80, stone=100)

    result = solver.solve_economy_balance(
        current_vills=current_vills,
        current_stockpile=stockpile,
        target_production={"knight": 2, "villager": 1},
        researched_techs=["double_bit_axe", "wheelbarrow", "horse_collar"],
        civ="franks",
    )

    assert result.optimal_allocation.total == 45
    assert result.optimal_allocation.food > current_vills.food
    assert result.optimal_allocation.gold > current_vills.gold
    assert result.optimal_allocation.wood < current_vills.wood
    # Should detect floating wood and low gold/food
    assert any("Floating" in b or "wood" in b.lower() for b in result.bottlenecks)
    assert len(result.actionable_rebalance_steps) > 0
