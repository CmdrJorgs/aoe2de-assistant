"""
Pydantic Request & Response Schemas for the AoE2 Coach FastAPI Gateway.
"""

from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class SnapshotInput(BaseModel):
    """
    Rapid input payload representing a player's mid-game snapshot.
    Designed for fast entry (<30 seconds) via sliders and visual selectors.
    """
    player_civ: str = Field(default="Franks", description="Player's civilization name or ID")
    opponent_civ: str = Field(default="Vikings", description="Opponent's civilization name or ID")
    player_elo: int = Field(default=1000, ge=400, le=3000, description="Player 1v1 ladder ELO")
    game_time_minutes: float = Field(default=18.0, ge=0.0, le=120.0, description="In-game time in minutes")
    current_age: int = Field(default=3, ge=1, le=4, description="1=Dark, 2=Feudal, 3=Castle, 4=Imperial")
    
    # Stockpile
    food: int = Field(default=300, ge=0, description="Current food stockpile")
    wood: int = Field(default=400, ge=0, description="Current wood stockpile")
    gold: int = Field(default=150, ge=0, description="Current gold stockpile")
    stone: int = Field(default=100, ge=0, description="Current stone stockpile")
    
    # Villager Allocations
    vills_food: int = Field(default=16, ge=0, description="Villagers on food")
    vills_wood: int = Field(default=14, ge=0, description="Villagers on wood")
    vills_gold: int = Field(default=6, ge=0, description="Villagers on gold")
    vills_stone: int = Field(default=2, ge=0, description="Villagers on stone")
    vills_total: Optional[int] = Field(default=None, ge=0, description="Total villagers (auto-computed if omitted)")
    
    # Military & Buildings
    military_units: Dict[str, int] = Field(default_factory=dict, description="Current player military units, e.g. {'Knight': 4}")
    player_buildings: Dict[str, int] = Field(default_factory=dict, description="Player production buildings, e.g. {'Stable': 2, 'Town Center': 2}")
    completed_techs: List[str] = Field(default_factory=list, description="Researched upgrades e.g. ['Bloodlines', 'Double-Bit Axe']")
    
    # Sighted Enemy Entities (Fog-of-War)
    sighted_enemy_units: Dict[str, int] = Field(default_factory=dict, description="Spotted enemy units, e.g. {'Berserk': 6}")
    sighted_enemy_buildings: Dict[str, int] = Field(default_factory=dict, description="Spotted enemy buildings, e.g. {'Castle': 1, 'Barracks': 2}")
    opponent_estimated_age: Optional[int] = Field(default=None, ge=1, le=4, description="Estimated opponent age (defaults to player age)")
    
    # Optional flags & context
    user_notes: Optional[str] = Field(default=None, description="Freeform notes or tactical focus")
    force_fallback: bool = Field(default=False, description="Force deterministic fallback explainer without calling LLM")
    elo_tier_override: Optional[str] = Field(default=None, description="Override ELO tier ('beginner', 'intermediate', 'advanced')")


class RecommendationResponse(BaseModel):
    """
    Unified coaching recommendation response combining ML, Domain Rules, and Verified Explanation.
    """
    match_context: Dict[str, Any]
    primary_directive: str
    win_probability: Dict[str, Any]
    military_action_plan: Dict[str, Any]
    counter_matrix: Dict[str, Any]
    economic_rebalance: Dict[str, Any]
    tactical_stance: Dict[str, Any]
    actionable_checklist: List[str]
    explanation: Dict[str, Any]
    inference_latency_ms: float
    explanation_latency_ms: float
    total_latency_ms: float


class CounterMatrixRequest(BaseModel):
    player_civ: str = "Franks"
    current_age: int = 3
    enemy_army: Dict[str, int] = Field(default_factory=lambda: {"Berserk": 5})
    budget_weight: str = Field(default="balanced", description="'cost_efficiency', 'raw_power', or 'balanced'")


class CounterMatrixResponse(BaseModel):
    player_civ: str
    current_age: int
    threat_analysis: List[Dict[str, Any]]
    recommended_counters: List[Dict[str, Any]]
    counter_compositions: List[Dict[str, Any]]


class ProductionGoal(BaseModel):
    unit_name: str
    building_count: int = 1


class EconomySolverRequest(BaseModel):
    civ: str = "Franks"
    current_age: int = 3
    production_goals: List[ProductionGoal] = Field(
        default_factory=lambda: [
            ProductionGoal(unit_name="Knight", building_count=2),
            ProductionGoal(unit_name="Villager", building_count=2),
        ]
    )
    researched_upgrades: List[str] = Field(
        default_factory=lambda: ["Wheelbarrow", "Double-Bit Axe", "Gold Mining"]
    )
    current_stockpile: Optional[Dict[str, int]] = None
    current_vills: Optional[Dict[str, int]] = None


class EconomySolverResponse(BaseModel):
    target_food_vills: int
    target_wood_vills: int
    target_gold_vills: int
    target_stone_vills: int
    total_target_vills: int
    resource_generation_rates: Dict[str, float]
    resource_consumption_rates: Dict[str, float]
    net_rates: Dict[str, float]
    delta_shifts: Dict[str, int]
    action_advice: List[str]


class VoiceParseRequest(BaseModel):
    transcript: str = Field(description="Spoken text from voice-to-text input")
    current_snapshot: Optional[SnapshotInput] = Field(default=None, description="Existing snapshot state to merge into")


class VoiceParseResponse(BaseModel):
    parsed_snapshot: SnapshotInput
    extracted_entities: Dict[str, Any]
    confidence_score: float
    feedback_message: str


class PresetScenario(BaseModel):
    id: str
    title: str
    description: str
    difficulty: str
    snapshot: SnapshotInput


class CombatSimRequest(BaseModel):
    attacker_unit: str = "Knight"
    attacker_count: int = 10
    attacker_civ: str = "Franks"
    attacker_upgrades: List[str] = Field(default_factory=list)
    
    defender_unit: str = "Pikeman"
    defender_count: int = 12
    defender_civ: str = "Vikings"
    defender_upgrades: List[str] = Field(default_factory=list)
    
    elevation_diff: int = Field(default=0, ge=-1, le=1, description="1=Attacker on hill, -1=Defender on hill, 0=Flat")


class CombatSimResponse(BaseModel):
    attacker_unit: str
    attacker_count: int
    defender_unit: str
    defender_count: int
    single_hit_attacker_to_defender: int
    single_hit_defender_to_attacker: int
    simulated_winner: str
    time_to_kill_seconds: float
    remaining_attackers: int
    remaining_defenders: int
    cost_efficiency_ratio: float
    tactical_summary: str


class HealthResponse(BaseModel):
    status: str
    version: str
    onnx_loaded: bool
    llm_connected: bool
    civs_count: int
    units_count: int
