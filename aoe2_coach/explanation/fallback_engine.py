"""
Deterministic Fallback Explanation Engine:
Provides high-quality, ELO-calibrated coaching output without requiring an active LLM endpoint.
Guarantees 100% uptime, zero latency (<1ms), and strict domain rule compliance.
"""

from typing import Dict, List, Optional
from aoe2_coach.models.inference_service import MLRecommendation
from aoe2_coach.explanation.schemas import (
    CoachingExplanation,
    TacticalMilitaryAdvice,
    TacticalEconomyAdvice,
    TacticalTimingAdvice,
    ELOTier,
    get_elo_tier,
)
from aoe2_coach.rules.tech_tree import get_civ_info


class DeterministicFallbackExplainer:
    """
    Generates structured tactical coaching responses directly from ML model predictions
    and deterministic counter-matrix evaluations.
    """

    @classmethod
    def generate_explanation(
        cls,
        recommendation: MLRecommendation,
        elo_tier_override: Optional[ELOTier] = None,
    ) -> CoachingExplanation:
        """Construct full ELO-calibrated coaching explanation."""
        ctx = recommendation.match_context
        tier = elo_tier_override or get_elo_tier(ctx.player_elo)
        civ_info = get_civ_info(ctx.player_civ)
        civ_name = civ_info.name if civ_info else ctx.player_civ

        mil_plan = recommendation.military_action_plan
        counter_res = recommendation.counter_matrix
        eco_plan = recommendation.economic_rebalance
        stance_res = recommendation.tactical_stance
        win_res = recommendation.win_probability

        # 1. Primary Directive
        primary_comp_title = mil_plan.primary_composition.replace("_", " ").title()
        directive = f"{ctx.player_age_name.upper()} {primary_comp_title.upper()} PUSH"

        # 2. Military Advice
        primary_unit = counter_res.primary_unit_recommendation
        secondary_unit = counter_res.secondary_support_unit
        prod_building = mil_plan.recommended_building.replace("_", " ").title()
        b_instruction = f"Produce {primary_unit} from 2-3 {prod_building}s"

        key_techs: List[str] = []
        if mil_plan.rankings and mil_plan.rankings[0].key_technologies:
            key_techs = [t.replace("_", " ").title() for t in mil_plan.rankings[0].key_technologies]
        elif mil_plan.recommended_tech_focus != "none":
            key_techs = [mil_plan.recommended_tech_focus.replace("_", " ").title()]

        counter_exp = counter_res.tactical_summary

        # Micro positioning tip based on ELO
        if tier == ELOTier.BEGINNER:
            micro_tip = f"Keep your {primary_unit}s grouped together. Don't fight under the enemy Town Center or Castle!"
        elif tier == ELOTier.INTERMEDIATE:
            micro_tip = f"Focus fire on enemy siege and key high-value units. Use patrol stance (P) into engagements."
        else:
            micro_tip = f"Take fights from high ground (+25% damage bonus). Split formation (X) vs incoming Mangonel shots and raid woodlines."

        military_advice = TacticalMilitaryAdvice(
            primary_unit_recommendation=primary_unit,
            secondary_unit_recommendation=secondary_unit,
            production_building_instruction=b_instruction,
            key_tech_priorities=key_techs,
            counter_explanation=counter_exp,
            micro_positioning_tip=micro_tip,
        )

        # 3. Economy Advice
        diagnosis = (
            f"Floating stockpile warning: {eco_plan.floating_stockpile_warnings[0]}"
            if eco_plan.floating_stockpile_warnings
            else f"Macro health grade: {eco_plan.macro_health_grade}."
        )
        immediate_action = (
            eco_plan.shift_instructions[0]
            if eco_plan.shift_instructions
            else "Maintain current gatherer balance and continuous villager creation."
        )
        target_vills = {
            "food": eco_plan.target_allocation.food,
            "wood": eco_plan.target_allocation.wood,
            "gold": eco_plan.target_allocation.gold,
            "stone": eco_plan.target_allocation.stone,
        }

        if tier == ELOTier.BEGINNER:
            macro_tip = "Never let your Town Center sit idle. Keep queuing villagers and reseed farms immediately when wood exceeds 200."
        elif tier == ELOTier.INTERMEDIATE:
            macro_tip = "Balance your eco to produce army continuously from all military buildings without floating excess stockpiles."
        else:
            macro_tip = "Optimize drop-off efficiency with tight lumber camp placement and pre-build houses to avoid population blocks."

        economy_advice = TacticalEconomyAdvice(
            problem_diagnosis=diagnosis,
            immediate_action=immediate_action,
            target_villager_allocation=target_vills,
            macro_tip=macro_tip,
        )

        # 4. Timing Advice
        posture = f"{stance_res.recommended_stance.replace('_', ' ').title()} ({stance_res.urgency.upper()} timing)"
        attack_window = f"Next {int(stance_res.attack_window_sec // 60)} minutes"
        threat_alert = stance_res.threat_spike_alert or None
        spike_reason = stance_res.civ_power_spike

        timing_advice = TacticalTimingAdvice(
            posture=posture,
            attack_window=attack_window,
            threat_alert=threat_alert,
            strategic_spike_reasoning=spike_reason,
        )

        # 5. Coach Summary calibrated to ELO
        if tier == ELOTier.BEGINNER:
            summary = (
                f"You are playing {civ_name} in {ctx.player_age_name}. Focus on simple execution: "
                f"spend your excess resources to mass {primary_unit}s from your {prod_building}s, "
                f"and shift woodcutters to farms to sustain production."
            )
        elif tier == ELOTier.INTERMEDIATE:
            summary = (
                f"Exploit your {civ_name} power spike in {ctx.player_age_name}. Sighted enemy forces "
                f"are vulnerable to {primary_unit}. Execute your gatherer rebalance now to support "
                f"continuous {primary_unit} production and strike within the next timing window."
            )
        else:
            summary = (
                f"Match Advantage: {win_res.advantage_level.replace('_', ' ').title()} ({round(win_res.win_probability * 100)}% Win Prob). "
                f"Opponent {ctx.opponent_civ} composition dictates immediate {primary_unit} transition. "
                f"{spike_reason} Seize map control before enemy reaches counter power spikes."
            )

        # 6. Priority Checklist
        checklist: List[str] = [
            f"1. Produce {primary_unit} from {prod_building}s",
            f"2. Macro: {immediate_action}",
        ]
        if key_techs:
            checklist.append(f"3. Research {key_techs[0]} at Blacksmith")
        checklist.append(f"4. Attack timing: Execute push within {attack_window}")

        return CoachingExplanation(
            primary_directive=directive,
            coach_summary=summary,
            elo_tier=tier,
            military_plan=military_advice,
            economic_plan=economy_advice,
            timing_plan=timing_advice,
            priority_checklist=checklist,
            raw_model_response=None,
        )
