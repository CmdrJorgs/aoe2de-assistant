"""
Pydantic Schemas for AoE2 LLM Tactical Explanation Engine:
Covers ELO Tiers, Tactical Advice, Hallucination Verification, and LLM Configurations.
"""

from enum import Enum
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field


class ELOTier(str, Enum):
    BEGINNER = "beginner"          # < 1000 ELO: Simple macro fundamentals, spend stockpile, basic counters
    INTERMEDIATE = "intermediate"  # 1000 - 1400 ELO: Strategic power spikes, tech order, relic & map control
    ADVANCED = "advanced"          # > 1400 ELO: Micro kiting, hill positioning, raid timings, army transitions


def get_elo_tier(elo: Optional[int]) -> ELOTier:
    """Determine player ELO coaching tier based on rating."""
    if elo is None or elo < 1000:
        return ELOTier.BEGINNER
    elif elo < 1400:
        return ELOTier.INTERMEDIATE
    else:
        return ELOTier.ADVANCED


class TacticalMilitaryAdvice(BaseModel):
    primary_unit_recommendation: str = Field(description="Primary unit to mass, e.g. 'Knight'")
    secondary_unit_recommendation: Optional[str] = Field(default=None, description="Optional secondary support unit, e.g. 'Monk'")
    production_building_instruction: str = Field(description="Target production buildings, e.g. 'Add 2 Stables for 3 total'")
    key_tech_priorities: List[str] = Field(default_factory=list, description="Ordered blacksmith/civ techs to research")
    counter_explanation: str = Field(description="Why this composition counters the observed enemy force")
    micro_positioning_tip: Optional[str] = Field(default=None, description="Tactical engagement or micro tip tailored to ELO")


class TacticalEconomyAdvice(BaseModel):
    problem_diagnosis: str = Field(description="Identified macro leak, e.g. 'Floating 750 wood while starving for food'")
    immediate_action: str = Field(description="Immediate villager reallocation order, e.g. 'Move 8 lumberjacks to build farms'")
    target_villager_allocation: Dict[str, int] = Field(
        default_factory=dict,
        description="Target villager distribution: {'food': X, 'wood': Y, 'gold': Z, 'stone': W}"
    )
    macro_tip: str = Field(description="Macro coaching advice tailored to player skill bracket")


class TacticalTimingAdvice(BaseModel):
    posture: str = Field(description="Game posture: e.g. 'Aggressive Castle Age Timing Push'")
    attack_window: str = Field(description="Critical timing window: e.g. 'Next 3-5 minutes'")
    threat_alert: Optional[str] = Field(default=None, description="Key opponent danger window or power spike warning")
    strategic_spike_reasoning: str = Field(description="Why this timing window exists based on civ matchups and age")


class CoachingExplanation(BaseModel):
    primary_directive: str = Field(description="High-impact directive header: e.g. 'CASTLE AGE CAVALRY PUSH'")
    coach_summary: str = Field(description="Engaging, natural coaching commentary calibrated to player ELO")
    elo_tier: ELOTier = Field(default=ELOTier.INTERMEDIATE)
    military_plan: TacticalMilitaryAdvice
    economic_plan: TacticalEconomyAdvice
    timing_plan: TacticalTimingAdvice
    priority_checklist: List[str] = Field(default_factory=list, description="Top 3-5 ordered action items to execute right now")
    raw_model_response: Optional[str] = Field(default=None, description="Raw unparsed LLM completion if available")


class HallucinationCheckResult(BaseModel):
    is_valid: bool = Field(default=True, description="Whether the response passed all tech tree and counter rules")
    violations: List[str] = Field(default_factory=list, description="List of rule violations detected")
    corrections_applied: List[str] = Field(default_factory=list, description="List of auto-corrections applied")
    sanitized_explanation: CoachingExplanation


class LLMConfig(BaseModel):
    base_url: str = Field(
        default="http://localhost:11434/v1",
        description="OpenAI API compatible endpoint base URL (e.g. Ollama http://localhost:11434/v1, llama.cpp http://localhost:8080/v1, vLLM, OpenAI)"
    )
    api_key: str = Field(
        default="ollama",
        description="API key for authentication (use 'ollama' or 'llama.cpp' for local endpoints)"
    )
    model: str = Field(
        default="llama3.2",
        description="Model name/identifier served by the local or remote endpoint"
    )
    temperature: float = Field(default=0.2, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1200, ge=100, le=4096)
    timeout_sec: float = Field(default=15.0, ge=1.0)
    response_format: Optional[str] = Field(default="json_object", description="'json_object' or None")


class VerifiedCoachingResponse(BaseModel):
    explanation: CoachingExplanation
    verification: HallucinationCheckResult
    elo_tier: ELOTier
    model_used: str
    generation_latency_ms: float
    total_pipeline_latency_ms: float
    was_fallback_used: bool = False
