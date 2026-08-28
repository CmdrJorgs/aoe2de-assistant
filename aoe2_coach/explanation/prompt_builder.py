"""
Prompt Engineering & Context Assembler for AoE2 LLM Coaching Engine:
Generates structured JSON prompts calibrated by player ELO tier (<1000, 1000-1400, >1400).
"""

import json
from typing import Dict, List, Optional, Any, Union
from aoe2_coach.schemas.game_constants import Age, get_civ_name
from aoe2_coach.models.inference_service import MLRecommendation
from aoe2_coach.explanation.schemas import ELOTier, get_elo_tier
from aoe2_coach.rules.tech_tree import get_civ_info


SYSTEM_PROMPT_TEMPLATE = """You are the Grandmaster AI Mid-Game Tactical Coach for Age of Empires II: Definitive Edition (AoE2:DE).
Your mission is to provide fast, high-impact, actionable tactical and strategic advice to the player based on their live match state, domain counter-matrix analysis, and machine learning predictions.

Strict Guidelines:
1. CIVILIZATION TECH TREE INTEGRITY:
   - Aztecs, Mayans, and Incas CANNOT build Stables or train Cavalry.
   - Britons CANNOT build Paladins.
   - Only recommend units, buildings, and technologies that the player's civilization can actually research and train at their current Age.
2. JSON OUTPUT FORMAT:
   - You MUST output ONLY a valid JSON object matching the exact schema specified below.
   - Do NOT include conversational preamble, markdown outside JSON, or trailing text.

JSON Output Schema:
{
  "primary_directive": "SHORT UPPERCASE TITLE (e.g. CASTLE AGE CAVALRY PUSH)",
  "coach_summary": "High-impact tactical coaching summary (2-3 sentences)",
  "military_plan": {
    "primary_unit_recommendation": "Unit name (e.g. Knight)",
    "secondary_unit_recommendation": "Secondary unit name or null",
    "production_building_instruction": "e.g. Add 2 Stables for 3 total Stables",
    "key_tech_priorities": ["Tech 1", "Tech 2"],
    "counter_explanation": "Clear explanation of why this counters sighted enemy units",
    "micro_positioning_tip": "Micro advice or tactical tip"
  },
  "economic_plan": {
    "problem_diagnosis": "Diagnosis of current stockpile / villager imbalance",
    "immediate_action": "Exact villager shift instruction",
    "target_villager_allocation": {
      "food": 0,
      "wood": 0,
      "gold": 0,
      "stone": 0
    },
    "macro_tip": "Practical economic habit advice"
  },
  "timing_plan": {
    "posture": "e.g. Aggressive Castle Age Timing Push",
    "attack_window": "e.g. Next 3-5 minutes",
    "threat_alert": "Opponent danger warning or null",
    "strategic_spike_reasoning": "Reason for this timing window"
  },
  "priority_checklist": [
    "1. Top priority action",
    "2. Second action",
    "3. Third action"
  ]
}

ELO Tier Guidance:
{elo_guidance}
"""

ELO_GUIDANCE_BEGINNER = """[COACHING BRACKET: BEGINNER (< 1000 ELO)]
- Keep explanations simple, encouraging, and easy to understand.
- Focus primarily on MACRO fundamentals: Spend floating resources, seed farms, build 2-3 production buildings, avoid being housed.
- Do not overload the player with complex micro commands or APM-heavy maneuvers.
- Explain unit counters in clear rock-paper-scissors terms (e.g. Spearmen beat Cavalry, Skirmishers beat Archers).
- Limit immediate action items to 1-2 major habits."""

ELO_GUIDANCE_INTERMEDIATE = """[COACHING BRACKET: INTERMEDIATE (1000 - 1400 ELO)]
- Provide balanced strategic and tactical advice.
- Emphasize civilization power spikes, blacksmith upgrade priority (e.g. armor vs attack), and economic rebalancing.
- Include timing windows, relic contestation, and proactive unit transitions.
- Focus on efficient gatherer reallocation and maintaining continuous production."""

ELO_GUIDANCE_ADVANCED = """[COACHING BRACKET: ADVANCED (> 1400 ELO)]
- Use concise, technical RTS terminology (power spikes, tech switches, hill bonus, choke points, kiting, split formations).
- Highlight micro positioning, line-of-sight denial, raiding exposed eco, and counter-siege maneuvers.
- Focus on precise timing windows, opponent tech transitions, and winning decisive military engagements."""


class PromptBuilder:
    """
    Constructs calibrated LLM prompts from match state and ML recommendations.
    """

    @classmethod
    def get_elo_guidance(cls, elo_tier: ELOTier) -> str:
        """Return coaching instructions for the specified ELO tier."""
        if elo_tier == ELOTier.BEGINNER:
            return ELO_GUIDANCE_BEGINNER
        elif elo_tier == ELOTier.ADVANCED:
            return ELO_GUIDANCE_ADVANCED
        return ELO_GUIDANCE_INTERMEDIATE

    @classmethod
    def build_system_prompt(cls, elo: Optional[int] = None, elo_tier: Optional[ELOTier] = None) -> str:
        """Construct the complete system prompt with ELO-calibrated instructions."""
        tier = elo_tier or get_elo_tier(elo)
        guidance = cls.get_elo_guidance(tier)
        return SYSTEM_PROMPT_TEMPLATE.replace("{elo_guidance}", guidance)

    @classmethod
    def build_user_prompt(
        cls,
        recommendation: MLRecommendation,
        user_notes: Optional[str] = None,
    ) -> str:
        """
        Assemble the structured user prompt containing match telemetry,
        ML model predictions, and deterministic counter-matrix evaluations.
        """
        ctx = recommendation.match_context
        civ_info = get_civ_info(ctx.player_civ)
        civ_bonuses_str = ", ".join(civ_info.civ_bonuses[:2]) if civ_info else "Standard bonuses"
        unique_units_str = ", ".join(civ_info.unique_units) if civ_info else "None"

        # Format sighted enemy forces
        sighted_enemy_desc = recommendation.counter_matrix.tactical_summary
        dominant_enemy = recommendation.counter_matrix.threat_analysis.dominant_enemy_unit
        threat_archetype = recommendation.counter_matrix.threat_analysis.primary_threat_archetype

        # Format eco rebalance
        eco = recommendation.economic_rebalance

        # Format military plan from ML
        mil = recommendation.military_action_plan
        top_techs = mil.rankings[0].key_technologies if mil.rankings else []
        if not top_techs and mil.recommended_tech_focus != "none":
            top_techs = [mil.recommended_tech_focus]
        techs_str = ", ".join(top_techs) if top_techs else "None"

        # Format win probability
        win = recommendation.win_probability

        # Format stance
        stance = recommendation.tactical_stance

        prompt_payload = {
            "match_context": {
                "player_civ": ctx.player_civ,
                "opponent_civ": ctx.opponent_civ,
                "player_elo": ctx.player_elo,
                "player_age": ctx.player_age_name,
                "game_time": ctx.formatted_time,
                "civ_specialties": civ_bonuses_str,
                "unique_units": unique_units_str,
            },
            "threat_analysis": {
                "dominant_enemy_unit": dominant_enemy,
                "threat_archetype": threat_archetype,
                "threat_level": recommendation.counter_matrix.threat_analysis.threat_level,
                "tactical_summary": sighted_enemy_desc,
                "warning": recommendation.counter_matrix.threat_analysis.tactical_warning or None,
            },
            "ml_strategic_prediction": {
                "recommended_composition": mil.primary_composition,
                "recommended_building": mil.recommended_building,
                "key_technologies": techs_str,
                "ml_confidence": f"{round(mil.confidence * 100, 1)}%",
                "ml_summary": mil.strategic_summary,
            },
            "economic_rebalancer": {
                "macro_health_grade": eco.macro_health_grade,
                "shift_instructions": eco.shift_instructions,
                "target_villagers": {
                    "food": eco.target_allocation.food,
                    "wood": eco.target_allocation.wood,
                    "gold": eco.target_allocation.gold,
                    "stone": eco.target_allocation.stone,
                },
                "villager_shifts": eco.villager_shifts,
                "floating_stockpile_warnings": eco.floating_stockpile_warnings,
            },
            "tactical_stance_and_timing": {
                "recommended_stance": stance.recommended_stance,
                "attack_window_seconds": stance.attack_window_sec,
                "urgency": stance.urgency,
                "civ_power_spike": stance.civ_power_spike,
                "threat_spike_alert": stance.threat_spike_alert or None,
            },
            "win_probability_estimation": {
                "win_rate": f"{round(win.win_probability * 100, 1)}%",
                "advantage_level": win.advantage_level,
                "key_factors": win.key_win_factors,
            },
        }

        if user_notes:
            prompt_payload["player_notes"] = user_notes

        return (
            "Analyze the following Age of Empires II match state and generate the tactical coaching advice JSON:\n\n"
            f"{json.dumps(prompt_payload, indent=2)}"
        )
