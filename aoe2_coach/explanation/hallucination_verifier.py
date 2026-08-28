"""
AoE2 Hallucination Verification & Tech Tree Guardrails Engine:
Validates LLM-generated tactical coaching against deterministic game rules,
civilization tech trees, counter matrices, and economic conservation laws.
Applies automated corrections when hallucinations are detected.
"""

import logging
from typing import Dict, List, Optional, Set, Tuple, Any
from aoe2_coach.schemas.game_constants import Age
from aoe2_coach.models.inference_service import MLRecommendation
from aoe2_coach.explanation.schemas import (
    CoachingExplanation,
    HallucinationCheckResult,
    TacticalMilitaryAdvice,
    TacticalEconomyAdvice,
    TacticalTimingAdvice,
)
from aoe2_coach.rules.tech_tree import (
    get_civ_info,
    is_unit_available,
    is_tech_available,
    is_building_available,
    TECHS_DATABASE,
)
from aoe2_coach.rules.units import UNITS_DATABASE, get_unit_stats

logger = logging.getLogger(__name__)


def _normalize_identifier(name: str) -> str:
    """Normalize a name to lower_snake_case for database lookups."""
    clean = name.lower().strip()
    clean = clean.replace(" ", "_").replace("-", "_")
    # Common suffix / plural cleanup
    if clean.endswith("s") and clean[:-1] in UNITS_DATABASE:
        clean = clean[:-1]
    if clean.endswith("men") and (clean[:-3] + "man") in UNITS_DATABASE:
        clean = clean[:-3] + "man"
    return clean


class HallucinationVerifier:
    """
    Validates coaching responses against hard AoE2 rules and auto-corrects hallucinations.
    """

    @classmethod
    def verify_and_sanitize(
        cls,
        explanation: CoachingExplanation,
        recommendation: MLRecommendation,
    ) -> HallucinationCheckResult:
        """
        Verify all fields of a coaching explanation against ground-truth game rules.
        Returns a HallucinationCheckResult with violation logs and sanitized output.
        """
        violations: List[str] = []
        corrections: List[str] = []

        ctx = recommendation.match_context
        player_civ = ctx.player_civ
        player_age_int = ctx.player_age
        age_enum = Age(player_age_int) if player_age_int in (1, 2, 3, 4) else Age.CASTLE
        civ_info = get_civ_info(player_civ)

        # Clone objects for sanitization
        mil = explanation.military_plan.model_copy()
        eco = explanation.economic_plan.model_copy()
        timing = explanation.timing_plan.model_copy()
        checklist = list(explanation.priority_checklist)

        # -------------------------------------------------------------
        # 1. Military Unit Validation (Tech Tree & Civ Restrictions)
        # -------------------------------------------------------------
        primary_id = _normalize_identifier(mil.primary_unit_recommendation)
        primary_valid = is_unit_available(player_civ, primary_id, age_enum)

        # Check for unique unit of another civ
        unit_stats = get_unit_stats(primary_id)
        if unit_stats and unit_stats.is_unique and unit_stats.civ:
            if civ_info and unit_stats.civ.lower() != civ_info.name.lower():
                primary_valid = False

        if not primary_valid:
            violation_msg = f"Illegal unit: '{mil.primary_unit_recommendation}' is not available to civilization '{player_civ}'."
            violations.append(violation_msg)
            
            # Auto-correct from counter matrix engine
            valid_primary = recommendation.counter_matrix.primary_unit_recommendation
            corrections.append(
                f"Replaced invalid unit '{mil.primary_unit_recommendation}' with civ-available unit '{valid_primary}'."
            )
            mil.primary_unit_recommendation = valid_primary
            mil.production_building_instruction = f"Produce {valid_primary} from {recommendation.military_action_plan.recommended_building.replace('_', ' ').title()}"

        # Validate secondary unit if present
        if mil.secondary_unit_recommendation:
            sec_id = _normalize_identifier(mil.secondary_unit_recommendation)
            sec_valid = is_unit_available(player_civ, sec_id, age_enum)
            sec_stats = get_unit_stats(sec_id)
            if sec_stats and sec_stats.is_unique and sec_stats.civ:
                if civ_info and sec_stats.civ.lower() != civ_info.name.lower():
                    sec_valid = False

            if not sec_valid:
                violations.append(f"Illegal secondary unit: '{mil.secondary_unit_recommendation}' is not available to '{player_civ}'.")
                mil.secondary_unit_recommendation = recommendation.counter_matrix.secondary_support_unit
                corrections.append(f"Auto-corrected secondary unit to '{mil.secondary_unit_recommendation}'.")

        # -------------------------------------------------------------
        # 2. Technology & Upgrade Validation (Civ Restrictions & Age)
        # -------------------------------------------------------------
        sanitized_techs: List[str] = []
        for tech in mil.key_tech_priorities:
            tech_id = _normalize_identifier(tech)
            tech_info = TECHS_DATABASE.get(tech_id)

            if tech_info:
                # Check civ availability
                if not is_tech_available(player_civ, tech_id):
                    violations.append(f"Illegal tech: '{tech}' is disabled for civilization '{player_civ}'.")
                    corrections.append(f"Removed unavailable tech '{tech}'.")
                    continue
                # Check age requirement
                if tech_info.age > age_enum:
                    violations.append(f"Premature tech: '{tech}' requires {tech_info.age.display_name} (player is in {age_enum.display_name}).")
                    corrections.append(f"Removed premature tech '{tech}'.")
                    continue
            sanitized_techs.append(tech)

        if not sanitized_techs and recommendation.military_action_plan.rankings and recommendation.military_action_plan.rankings[0].key_technologies:
            fallback_tech = recommendation.military_action_plan.rankings[0].key_technologies[0].replace("_", " ").title()
            sanitized_techs.append(fallback_tech)
            corrections.append(f"Added ground-truth tech priority '{fallback_tech}'.")

        mil.key_tech_priorities = sanitized_techs

        # -------------------------------------------------------------
        # 3. Economic Allocation Conservation Validation
        # -------------------------------------------------------------
        current_total_vills = recommendation.economic_rebalance.current_allocation.total

        target_alloc = eco.target_villager_allocation or {}
        food_v = max(0, int(target_alloc.get("food", 0)))
        wood_v = max(0, int(target_alloc.get("wood", 0)))
        gold_v = max(0, int(target_alloc.get("gold", 0)))
        stone_v = max(0, int(target_alloc.get("stone", 0)))
        target_sum = food_v + wood_v + gold_v + stone_v

        # Check for severe mismatch with actual villager population (> 4 vills disparity)
        if current_total_vills > 0 and abs(target_sum - current_total_vills) > 4:
            violations.append(
                f"Economic math violation: Target villagers total ({target_sum}) does not match player total ({current_total_vills})."
            )
            eco.target_villager_allocation = {
                "food": recommendation.economic_rebalance.target_allocation.food,
                "wood": recommendation.economic_rebalance.target_allocation.wood,
                "gold": recommendation.economic_rebalance.target_allocation.gold,
                "stone": recommendation.economic_rebalance.target_allocation.stone,
            }
            corrections.append("Re-synchronized target villager allocation with linear solver output.")

        # -------------------------------------------------------------
        # 4. Priority Checklist & Directives Validation
        # -------------------------------------------------------------
        if not checklist:
            checklist = [
                f"1. Produce {mil.primary_unit_recommendation} from {recommendation.military_action_plan.recommended_building.replace('_', ' ').title()}",
                f"2. Macro: {eco.immediate_action}",
                f"3. Timing: {timing.posture} ({timing.attack_window})",
            ]
            corrections.append("Generated missing priority checklist from validated plans.")

        # Reconstruct sanitized CoachingExplanation
        sanitized_exp = CoachingExplanation(
            primary_directive=explanation.primary_directive or f"{ctx.player_age_name.upper()} MILITARY PUSH",
            coach_summary=explanation.coach_summary,
            elo_tier=explanation.elo_tier,
            military_plan=mil,
            economic_plan=eco,
            timing_plan=timing,
            priority_checklist=checklist,
            raw_model_response=explanation.raw_model_response,
        )

        is_valid = len(violations) == 0

        return HallucinationCheckResult(
            is_valid=is_valid,
            violations=violations,
            corrections_applied=corrections,
            sanitized_explanation=sanitized_exp,
        )
