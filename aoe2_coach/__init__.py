"""
AoE2 Coach: Real-Time AI Strategy & Tactical Coaching Engine for Age of Empires II: DE.
"""

from aoe2_coach.explanation import (
    TacticalExplanationEngine,
    DeterministicFallbackExplainer,
    HallucinationVerifier,
    PromptBuilder,
    OpenAICompatibleLLMClient,
    LLMConfig,
    ELOTier,
    get_elo_tier,
    CoachingExplanation,
    VerifiedCoachingResponse,
)

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent

__version__ = "0.1.0"

__all__ = [
    "TacticalExplanationEngine",
    "DeterministicFallbackExplainer",
    "HallucinationVerifier",
    "PromptBuilder",
    "OpenAICompatibleLLMClient",
    "LLMConfig",
    "ELOTier",
    "get_elo_tier",
    "CoachingExplanation",
    "VerifiedCoachingResponse",
]
