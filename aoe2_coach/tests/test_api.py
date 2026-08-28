"""
FastAPI Integration Tests for AoE2 Coach Gateway.
"""

import pytest
from fastapi.testclient import TestClient
from aoe2_coach.api.app import app
from aoe2_coach.api.presets import PRESET_SCENARIOS


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["civs_count"] >= 45
    assert data["units_count"] >= 30


def test_get_civs_and_units_metadata(client: TestClient):
    # Civs
    r_civs = client.get("/api/meta/civs")
    assert r_civs.status_code == 200
    civs = r_civs.json()
    assert len(civs) >= 45
    franks = next((c for c in civs if c["name"] == "Franks"), None)
    assert franks is not None
    assert any("throwing" in u.lower() for u in franks["unique_units"])

    # Units
    r_units = client.get("/api/meta/units")
    assert r_units.status_code == 200
    units = r_units.json()
    assert len(units) >= 30
    knight = next((u for u in units if u["name"] == "Knight"), None)
    assert knight is not None
    assert knight["category"] == "cavalry"


def test_get_presets(client: TestClient):
    response = client.get("/api/meta/presets")
    assert response.status_code == 200
    presets = response.json()
    assert len(presets) >= 4
    preset_id = presets[0]["id"]

    r_single = client.get(f"/api/meta/presets/{preset_id}")
    assert r_single.status_code == 200
    assert r_single.json()["id"] == preset_id


def test_tactical_recommendation_endpoint(client: TestClient):
    payload = {
        "player_civ": "Franks",
        "opponent_civ": "Vikings",
        "player_elo": 950,
        "game_time_minutes": 22.5,
        "current_age": 3,
        "food": 320,
        "wood": 750,
        "gold": 120,
        "stone": 450,
        "vills_food": 14,
        "vills_wood": 26,
        "vills_gold": 6,
        "vills_stone": 2,
        "sighted_enemy_units": {"Berserk": 5},
        "sighted_enemy_buildings": {"Castle": 1},
        "force_fallback": True,
    }
    response = client.post("/api/tactical/recommend", json=payload)
    assert response.status_code == 200
    data = response.json()
    
    assert "primary_directive" in data
    assert "military_action_plan" in data
    assert "economic_rebalance" in data
    assert "counter_matrix" in data
    assert "tactical_stance" in data
    assert "explanation" in data
    assert len(data["actionable_checklist"]) > 0
    assert data["inference_latency_ms"] >= 0


def test_counter_matrix_endpoint(client: TestClient):
    payload = {
        "player_civ": "Britons",
        "current_age": 3,
        "enemy_army": {"Knight": 10},
        "budget_weight": "cost_efficiency",
    }
    response = client.post("/api/tactical/counter-matrix", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert len(data["recommended_counters"]) > 0
    assert any("Pikeman" in c["unit_name"] or "Monk" in c["unit_name"] for c in data["recommended_counters"])


def test_economy_solver_endpoint(client: TestClient):
    payload = {
        "civ": "Franks",
        "current_age": 3,
        "production_goals": [
            {"unit_name": "Knight", "building_count": 2},
            {"unit_name": "Villager", "building_count": 1},
        ],
        "researched_upgrades": ["Wheelbarrow", "Double-Bit Axe", "Gold Mining"],
        "current_vills": {"food": 10, "wood": 25, "gold": 4, "stone": 0},
    }
    response = client.post("/api/tactical/economy-solver", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_food_vills"] > 0
    assert data["target_gold_vills"] > 0
    assert data["total_target_vills"] > 0
    assert len(data["action_advice"]) > 0


def test_voice_parse_endpoint(client: TestClient):
    payload = {
        "transcript": "Playing Franks against Vikings, I have 800 wood and 200 food and I see 5 berserks",
    }
    response = client.post("/api/tactical/voice-parse", json=payload)
    assert response.status_code == 200
    data = response.json()
    snap = data["parsed_snapshot"]
    assert snap["player_civ"] == "Franks"
    assert snap["opponent_civ"] == "Vikings"
    assert snap["wood"] == 800
    assert snap["food"] == 200
    assert "Berserk" in snap["sighted_enemy_units"]


def test_combat_simulation_endpoint(client: TestClient):
    payload = {
        "attacker_unit": "Knight",
        "attacker_count": 10,
        "attacker_civ": "Franks",
        "defender_unit": "Pikeman",
        "defender_count": 15,
        "defender_civ": "Vikings",
        "elevation_diff": 0,
    }
    response = client.post("/api/tactical/simulate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["single_hit_defender_to_attacker"] > 15  # Bonus vs cavalry
    assert data["simulated_winner"] in ["Knight", "Pikeman", "Attacker", "Defender", "Draw"]
