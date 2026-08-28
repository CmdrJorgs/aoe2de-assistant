"""
AoE2 LLM Explanation & Tactical Coaching Package:
Provides OpenAI-compatible LLM coaching, ELO tier calibration, prompt building,
deterministic fallback explainer, and hallucination verification against AoE2 game rules.
"""

from aoe2_coach.explanation.schemas import (
    ELOTier,
    get_elo_tier,
    TacticalMilitaryAdvice,
    TacticalEconomyAdvice,
    TacticalTimingAdvice,
    CoachingExplanation,
    HallucinationCheckResult,
    LLMConfig,
    VerifiedCoachingResponse,
)
from aoe2_coach.explanation.prompt_builder import PromptBuilder
from aoe2_coach.explanation.client import (
    OpenAICompatibleLLMClient,
    extract_json_from_text,
)
from aoe2_coach.explanation.fallback_engine import DeterministicFallbackExplainer
from aoe2_coach.explanation.hallucination_verifier import HallucinationVerifier
from aoe2_coach.explanation.engine import TacticalExplanationEngine

__all__ = [
    "ELOTier",
    "get_elo_tier",
    "TacticalMilitaryAdvice",
    "TacticalEconomyAdvice",
    "TacticalTimingAdvice",
    "CoachingExplanation",
    "HallucinationCheckResult",
    "LLMConfig",
    "VerifiedCoachingResponse",
    "PromptBuilder",
    "OpenAICompatibleLLMClient",
    "extract_json_from_text",
    "DeterministicFallbackExplainer",
    "HallucinationVerifier",
    "TacticalExplanationEngine",
]
