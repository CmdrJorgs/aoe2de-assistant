"""
AoE2 Unified Tactical Explanation Engine:
Orchestrates prompt creation, OpenAI-compatible LLM inference (llama.cpp/Ollama/vLLM/OpenAI),
automatic fallback handling, and deterministic hallucination verification.
"""

import time
import logging
from typing import Dict, List, Optional, Any, Tuple, Union

from aoe2_coach.models.inference_service import MLRecommendation
from aoe2_coach.explanation.schemas import (
    CoachingExplanation,
    VerifiedCoachingResponse,
    HallucinationCheckResult,
    LLMConfig,
    ELOTier,
    get_elo_tier,
)
from aoe2_coach.explanation.prompt_builder import PromptBuilder
from aoe2_coach.explanation.client import OpenAICompatibleLLMClient
from aoe2_coach.explanation.fallback_engine import DeterministicFallbackExplainer
from aoe2_coach.explanation.hallucination_verifier import HallucinationVerifier

logger = logging.getLogger(__name__)


class TacticalExplanationEngine:
    """
    Main explanation and coaching service.
    Translates raw ML & rule outputs into ELO-calibrated, verified natural language advice.
    """

    def __init__(
        self,
        config: Optional[LLMConfig] = None,
        client: Optional[OpenAICompatibleLLMClient] = None,
        force_fallback: bool = False,
    ):
        self.config = config or LLMConfig()
        self.client = client or OpenAICompatibleLLMClient(self.config)
        self.force_fallback = force_fallback

    def explain(
        self,
        recommendation: MLRecommendation,
        elo_override: Optional[int] = None,
        user_notes: Optional[str] = None,
        force_fallback: Optional[bool] = None,
        config_override: Optional[LLMConfig] = None,
    ) -> VerifiedCoachingResponse:
        """
        Generate structured, verified coaching response synchronously.
        """
        start_time = time.perf_counter()
        use_fallback = self.force_fallback if force_fallback is None else force_fallback
        cfg = config_override or self.config

        effective_elo = elo_override if elo_override is not None else recommendation.match_context.player_elo
        elo_tier = get_elo_tier(effective_elo)

        gen_latency_ms = 0.0
        was_fallback = False
        raw_text: Optional[str] = None
        explanation: Optional[CoachingExplanation] = None

        if not use_fallback:
            try:
                system_prompt = PromptBuilder.build_system_prompt(elo=effective_elo, elo_tier=elo_tier)
                user_prompt = PromptBuilder.build_user_prompt(recommendation, user_notes=user_notes)

                parsed_json, raw_text, gen_latency_ms = self.client.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    config_override=cfg,
                )

                # Validate parsed JSON into CoachingExplanation schema
                parsed_json["elo_tier"] = elo_tier.value
                parsed_json["raw_model_response"] = raw_text
                explanation = CoachingExplanation.model_validate(parsed_json)

            except Exception as e:
                logger.warning(f"LLM generation failed or timed out: {e}. Utilizing deterministic fallback engine.")
                was_fallback = True
        else:
            was_fallback = True

        # If LLM was skipped or failed, use deterministic fallback explainer
        if explanation is None or was_fallback:
            was_fallback = True
            t0 = time.perf_counter()
            explanation = DeterministicFallbackExplainer.generate_explanation(
                recommendation,
                elo_tier_override=elo_tier,
            )
            gen_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        # Hallucination and Tech-Tree Verification Layer
        verification_result = HallucinationVerifier.verify_and_sanitize(
            explanation=explanation,
            recommendation=recommendation,
        )

        total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return VerifiedCoachingResponse(
            explanation=verification_result.sanitized_explanation,
            verification=verification_result,
            elo_tier=elo_tier,
            model_used=cfg.model if not was_fallback else "deterministic_fallback_v1",
            generation_latency_ms=gen_latency_ms,
            total_pipeline_latency_ms=total_latency_ms,
            was_fallback_used=was_fallback,
        )

    async def async_explain(
        self,
        recommendation: MLRecommendation,
        elo_override: Optional[int] = None,
        user_notes: Optional[str] = None,
        force_fallback: Optional[bool] = None,
        config_override: Optional[LLMConfig] = None,
    ) -> VerifiedCoachingResponse:
        """
        Generate structured, verified coaching response asynchronously.
        """
        start_time = time.perf_counter()
        use_fallback = self.force_fallback if force_fallback is None else force_fallback
        cfg = config_override or self.config

        effective_elo = elo_override if elo_override is not None else recommendation.match_context.player_elo
        elo_tier = get_elo_tier(effective_elo)

        gen_latency_ms = 0.0
        was_fallback = False
        raw_text: Optional[str] = None
        explanation: Optional[CoachingExplanation] = None

        if not use_fallback:
            try:
                system_prompt = PromptBuilder.build_system_prompt(elo=effective_elo, elo_tier=elo_tier)
                user_prompt = PromptBuilder.build_user_prompt(recommendation, user_notes=user_notes)

                parsed_json, raw_text, gen_latency_ms = await self.client.async_generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    config_override=cfg,
                )

                parsed_json["elo_tier"] = elo_tier.value
                parsed_json["raw_model_response"] = raw_text
                explanation = CoachingExplanation.model_validate(parsed_json)

            except Exception as e:
                logger.warning(f"Async LLM generation failed: {e}. Utilizing deterministic fallback engine.")
                was_fallback = True
        else:
            was_fallback = True

        if explanation is None or was_fallback:
            was_fallback = True
            t0 = time.perf_counter()
            explanation = DeterministicFallbackExplainer.generate_explanation(
                recommendation,
                elo_tier_override=elo_tier,
            )
            gen_latency_ms = round((time.perf_counter() - t0) * 1000.0, 2)

        verification_result = HallucinationVerifier.verify_and_sanitize(
            explanation=explanation,
            recommendation=recommendation,
        )

        total_latency_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        return VerifiedCoachingResponse(
            explanation=verification_result.sanitized_explanation,
            verification=verification_result,
            elo_tier=elo_tier,
            model_used=cfg.model if not was_fallback else "deterministic_fallback_v1",
            generation_latency_ms=gen_latency_ms,
            total_pipeline_latency_ms=total_latency_ms,
            was_fallback_used=was_fallback,
        )
