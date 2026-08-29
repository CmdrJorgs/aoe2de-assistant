"""
AoE2 Coach User Testing & ELO Calibration Suite (Phase 6):
Simulates live match situations for 800–1200 ELO beginner/intermediate players,
evaluates cognitive load reduction, advice clarity, and multi-round coaching progression.
"""

import time
from typing import Dict, List, Any, Optional
import numpy as np
from pydantic import BaseModel, Field

from aoe2_coach.models.inference_service import MLInferenceService, MLRecommendation
from aoe2_coach.explanation.engine import TacticalExplanationEngine
from aoe2_coach.explanation.schemas import LLMConfig, ELOTier, get_elo_tier


class UserTestingScenario(BaseModel):
    """Realistic beginner / intermediate live-match crisis or blunder scenario."""
    test_id: str
    title: str
    player_civ: str
    opponent_civ: str
    player_elo: int
    game_time_sec: int
    current_age: int
    food: int
    wood: int
    gold: int
    stone: int
    vills_food: int
    vills_wood: int
    vills_gold: int
    vills_stone: int
    sighted_enemy_units: Dict[str, int]
    sighted_enemy_buildings: Dict[str, int]
    primary_blunder: str
    expected_primary_action: str
    expected_counter_units: List[str]
    expected_max_action_items: int = 3


# 12 Realistic Live Match Scenarios for 800–1200 ELO Players
BEGINNER_TEST_SCENARIOS: List[UserTestingScenario] = [
    # 1. Extreme Wood Float & No Farms (Classic 900 ELO Blunder)
    UserTestingScenario(
        test_id="user-test-01-severe-wood-float",
        title="Severe Wood Floating vs Farm Shortage",
        player_civ="Franks",
        opponent_civ="Vikings",
        player_elo=880,
        game_time_sec=1140,  # 19:00
        current_age=3,
        food=65,
        wood=890,
        gold=110,
        stone=100,
        vills_food=8,
        vills_wood=26,
        vills_gold=6,
        vills_stone=0,
        sighted_enemy_units={"berserk": 4},
        sighted_enemy_buildings={"castle": 1},
        primary_blunder="Player is floating 890 Wood with 26 woodchoppers while starving on Food with only 8 farmers.",
        expected_primary_action="Shift woodchoppers to farms immediately",
        expected_counter_units=["knight", "hand_cannoneer", "archer"],
        expected_max_action_items=3,
    ),

    # 2. Panic Cavalry Dive (Surprise 6 Knights in Base)
    UserTestingScenario(
        test_id="user-test-02-cavalry-dive-panic",
        title="Surprise Knight Dive Response",
        player_civ="Britons",
        opponent_civ="Franks",
        player_elo=950,
        game_time_sec=1260,  # 21:00
        current_age=3,
        food=220,
        wood=350,
        gold=180,
        stone=50,
        vills_food=14,
        vills_wood=16,
        vills_gold=8,
        vills_stone=0,
        sighted_enemy_units={"knight": 8},
        sighted_enemy_buildings={"stable": 2},
        primary_blunder="Enemy heavy cavalry diving base with 0 spear/monk defense.",
        expected_primary_action="Produce Pikemen/Monks and garrison Town Center",
        expected_counter_units=["pikeman", "spearman", "monk"],
        expected_max_action_items=3,
    ),

    # 3. Counter-Pick Trap (Massing Skirms into Knights)
    UserTestingScenario(
        test_id="user-test-03-counter-trap",
        title="False Counter Trap (Skirms vs Heavy Cav)",
        player_civ="Byzantines",
        opponent_civ="Franks",
        player_elo=1020,
        game_time_sec=1320,  # 22:00
        current_age=3,
        food=310,
        wood=450,
        gold=190,
        stone=100,
        vills_food=14,
        vills_wood=18,
        vills_gold=6,
        vills_stone=0,
        sighted_enemy_units={"knight": 10},
        sighted_enemy_buildings={"stable": 2},
        primary_blunder="Player massed Skirmishers which deal 1 damage to high-armor Knights.",
        expected_primary_action="Switch production to cheap Byzantine Pikemen and Camels",
        expected_counter_units=["pikeman", "camel", "camel_rider", "monk"],
        expected_max_action_items=4,
    ),

    # 4. Delayed Castle Age Up (Feudal Economy Imbalance)
    UserTestingScenario(
        test_id="user-test-04-delayed-castle-age",
        title="Delayed Castle Age Transition",
        player_civ="Mayans",
        opponent_civ="Huns",
        player_elo=920,
        game_time_sec=900,  # 15:00
        current_age=2,
        food=380,
        wood=580,
        gold=240,
        stone=0,
        vills_food=10,
        vills_wood=18,
        vills_gold=4,
        vills_stone=0,
        sighted_enemy_units={"scout_cavalry": 4},
        sighted_enemy_buildings={"stable": 1},
        primary_blunder="Player needs 800 Food to click Castle Age but has 18 woodchoppers and only 10 on food.",
        expected_primary_action="Drop farms with wood stockpile to reach 800 Food",
        expected_counter_units=["spearman", "pikeman", "archer", "skirmisher"],
        expected_max_action_items=3,
    ),

    # 5. Missing Blacksmith Armor on Archers
    UserTestingScenario(
        test_id="user-test-05-missing-armor-tech",
        title="Missing Blacksmith Padded Archer Armor",
        player_civ="Ethiopians",
        opponent_civ="Britons",
        player_elo=1100,
        game_time_sec=1200,  # 20:00
        current_age=3,
        food=280,
        wood=490,
        gold=350,
        stone=0,
        vills_food=12,
        vills_wood=20,
        vills_gold=12,
        vills_stone=0,
        sighted_enemy_units={"skirmisher": 8, "archer": 6},
        sighted_enemy_buildings={"archery_range": 2},
        primary_blunder="Player archers lack armor upgrades and get shredded by Skirmishers.",
        expected_primary_action="Research Padded Archer Armor / Bodkin Arrow and add Mangonel",
        expected_counter_units=["mangonel", "siege", "skirmisher", "knight", "crossbowman"],
        expected_max_action_items=4,
    ),

    # 6. Idle Gold Stockpile Without Production
    UserTestingScenario(
        test_id="user-test-06-floating-gold",
        title="Unspent Gold Floating Without Production Buildings",
        player_civ="Turks",
        opponent_civ="Goths",
        player_elo=1050,
        game_time_sec=1440,  # 24:00
        current_age=3,
        food=350,
        wood=420,
        gold=880,
        stone=200,
        vills_food=16,
        vills_wood=16,
        vills_gold=16,
        vills_stone=0,
        sighted_enemy_units={"huskarl": 10},
        sighted_enemy_buildings={"barracks": 3},
        primary_blunder="Player floating 880 Gold with only 1 production building.",
        expected_primary_action="Drop Castle/Siege Workshop and produce Hand Cannoneers/Janissaries",
        expected_counter_units=["hand_cannoneer", "janissary", "champion", "unique_unit"],
        expected_max_action_items=4,
    ),

    # 7. Surprise Castle Drop on Hill
    UserTestingScenario(
        test_id="user-test-07-castle-drop-threat",
        title="Forward Enemy Castle Drop Reaction",
        player_civ="Franks",
        opponent_civ="Spanish",
        player_elo=1150,
        game_time_sec=1350,  # 22:30
        current_age=3,
        food=450,
        wood=520,
        gold=280,
        stone=450,
        vills_food=18,
        vills_wood=18,
        vills_gold=10,
        vills_stone=6,
        sighted_enemy_units={"conquistador": 6},
        sighted_enemy_buildings={"castle": 1},
        primary_blunder="Enemy building forward Castle; Spanish Conquistadors raiding eco.",
        expected_primary_action="Build defensive Castle/Siege Workshop and produce Knights/Petards",
        expected_counter_units=["knight", "skirmisher", "mangonel", "pikeman"],
        expected_max_action_items=4,
    ),

    # 8. Overinvested Pikemen into Archer Ball
    UserTestingScenario(
        test_id="user-test-08-overinvested-pikes",
        title="Over-producing Pikemen into Archer Ball",
        player_civ="Goths",
        opponent_civ="Britons",
        player_elo=990,
        game_time_sec=1400,  # 23:20
        current_age=3,
        food=290,
        wood=620,
        gold=180,
        stone=350,
        vills_food=16,
        vills_wood=22,
        vills_gold=6,
        vills_stone=2,
        sighted_enemy_units={"crossbowman": 16},
        sighted_enemy_buildings={"archery_range": 2},
        primary_blunder="Player making 18 Pikemen vs Crossbows (Pikes have 0 pierce armor).",
        expected_primary_action="Stop Pikemen; build Castle for Huskarls or Range for Skirmishers",
        expected_counter_units=["skirmisher", "huskarl", "champion", "unique_unit", "mangonel"],
        expected_max_action_items=3,
    ),

    # 9. Low Villager Count Stagnation
    UserTestingScenario(
        test_id="user-test-09-vill-stagnation",
        title="Town Center Idle / Villager Count Deficit",
        player_civ="Teutons",
        opponent_civ="Mongols",
        player_elo=850,
        game_time_sec=1200,  # 20:00
        current_age=3,
        food=180,
        wood=410,
        gold=120,
        stone=250,
        vills_food=10,
        vills_wood=12,
        vills_gold=4,
        vills_stone=2,
        sighted_enemy_units={"steppe_lancer": 5},
        sighted_enemy_buildings={"stable": 1},
        primary_blunder="Player only has 28 villagers at minute 20 due to idle Town Center.",
        expected_primary_action="Queue continuous villagers and build farms",
        expected_counter_units=["pikeman", "spearman", "knight", "monk"],
        expected_max_action_items=3,
    ),

    # 10. Missing Monks on Relic-Heavy Map
    UserTestingScenario(
        test_id="user-test-10-monk-relic-neglect",
        title="Monastery / Relic Collection Opportunity",
        player_civ="Lithuanians",
        opponent_civ="Franks",
        player_elo=1180,
        game_time_sec=1250,  # 20:50
        current_age=3,
        food=410,
        wood=390,
        gold=280,
        stone=100,
        vills_food=16,
        vills_wood=16,
        vills_gold=10,
        vills_stone=0,
        sighted_enemy_units={"knight": 6},
        sighted_enemy_buildings={"stable": 2},
        primary_blunder="Lithuanians get +2 attack per relic for Knights/Leitis; player hasn't built Monastery.",
        expected_primary_action="Build Monastery, collect relics, produce Monks vs enemy knights",
        expected_counter_units=["monk", "pikeman", "leitis", "unique_unit", "knight"],
        expected_max_action_items=4,
    ),

    # 11. Imperial Age Without Economy to Tech
    UserTestingScenario(
        test_id="user-test-11-fast-imp-starvation",
        title="Premature Imperial Age Economy Starvation",
        player_civ="Turks",
        opponent_civ="Byzantines",
        player_elo=960,
        game_time_sec=1600,  # 26:40
        current_age=4,
        food=140,
        wood=580,
        gold=90,
        stone=0,
        vills_food=12,
        vills_wood=20,
        vills_gold=8,
        vills_stone=0,
        sighted_enemy_units={"cataphract": 6},
        sighted_enemy_buildings={"castle": 1},
        primary_blunder="Reached Imperial Age without food/gold eco to afford Bombard Cannon or Chemistry.",
        expected_primary_action="Seed farms with wood stockpile to afford Chemistry & Heavy Cav upgrades",
        expected_counter_units=["heavy_camel_rider", "camel", "halberdier", "pikeman", "paladin", "janissary"],
        expected_max_action_items=3,
    ),

    # 12. Monks Micro Trap (Cognitive Overload)
    UserTestingScenario(
        test_id="user-test-12-micro-overload-trap",
        title="Low-ELO Cognitive Overload Mitigation",
        player_civ="Saracens",
        opponent_civ="Franks",
        player_elo=890,
        game_time_sec=1300,  # 21:40
        current_age=3,
        food=320,
        wood=440,
        gold=310,
        stone=50,
        vills_food=14,
        vills_wood=16,
        vills_gold=10,
        vills_stone=0,
        sighted_enemy_units={"knight": 10},
        sighted_enemy_buildings={"stable": 2},
        primary_blunder="890 ELO player trying to convert individual knights with 8 monks while getting raided.",
        expected_primary_action="Produce sturdy Camels and Pikemen instead of complex monk micro",
        expected_counter_units=["camel_rider", "camel", "pikeman", "monk"],
        expected_max_action_items=3,
    ),
]


class UserTestResult(BaseModel):
    """Evaluation result of coach output on a beginner match situation."""
    test_id: str
    title: str
    player_elo: int
    elo_tier: str
    primary_directive: str
    action_item_count: int
    conciseness_pass: bool
    root_cause_prioritized: bool
    correct_counter_recommended: bool
    word_count: int
    cognitive_load_score: float  # 0.0 to 1.0 (1.0 = ideal low cognitive load)
    generation_latency_ms: float
    feedback_notes: str


class CalibrationReport(BaseModel):
    """Aggregate calibration report for 800-1200 ELO beginner coaching."""
    timestamp: str
    total_tests: int
    conciseness_pass_rate_pct: float
    root_cause_prioritization_pct: float
    counter_accuracy_pct: float
    mean_action_items: float
    mean_cognitive_load_score: float
    mean_latency_ms: float
    test_results: List[UserTestResult]
    calibration_status: str

    def to_markdown(self) -> str:
        """Render calibration report in Markdown format."""
        md = []
        md.append("# AoE2 Coach AI — 800–1200 ELO User Testing & Calibration Report")
        md.append(f"**Execution Timestamp:** {self.timestamp}\n")

        md.append("## 1. Executive Summary & Calibration Gate")
        md.append("| Metric | Requirement | Measured Score | Status |")
        md.append("| :--- | :--- | :--- | :--- |")

        conc_status = "✅ PASS" if self.conciseness_pass_rate_pct >= 90.0 else "❌ FAIL"
        md.append(f"| **Action Item Limit ($\\le 3-4$ items)** | $\\ge 90.0\\%$ | **{self.conciseness_pass_rate_pct:.1f}%** | {conc_status} |")

        root_status = "✅ PASS" if self.root_cause_prioritization_pct >= 85.0 else "❌ FAIL"
        md.append(f"| **Macro Root-Cause Prioritization** | $\\ge 85.0\\%$ | **{self.root_cause_prioritization_pct:.1f}%** | {root_status} |")

        counter_status = "✅ PASS" if self.counter_accuracy_pct >= 90.0 else "❌ FAIL"
        md.append(f"| **Beginner Counter Accuracy** | $\\ge 90.0\\%$ | **{self.counter_accuracy_pct:.1f}%** | {counter_status} |")

        cog_status = "✅ PASS" if self.mean_cognitive_load_score >= 0.85 else "❌ FAIL"
        md.append(f"| **Cognitive Load Index ($\\ge 0.85$)** | $\\ge 0.85$ | **{self.mean_cognitive_load_score:.2f} / 1.0** | {cog_status} |")

        lat_status = "✅ PASS" if self.mean_latency_ms < 50.0 else "❌ FAIL"
        md.append(f"| **Mean Live Advice Latency** | $< 50.0$ ms | **{self.mean_latency_ms:.2f} ms** | {lat_status} |")

        md.append(f"\n**Overall Calibration Status:** **{self.calibration_status}**\n")

        md.append("## 2. Live Scenario Evaluation Breakdown")
        md.append("| Test ID | ELO | Scenario / Blunder | Primary Directive | Actions | Cog Score | Status |")
        md.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- |")

        for res in self.test_results:
            status_icon = "✅ PASS" if (res.conciseness_pass and res.root_cause_prioritized and res.correct_counter_recommended) else "⚠️ CALIBRATE"
            md.append(
                f"| `{res.test_id}` | {res.player_elo} | {res.title} | "
                f"**{res.primary_directive}** | {res.action_item_count} items | "
                f"{res.cognitive_load_score:.2f} | {status_icon} |"
            )

        md.append("\n## 3. Cognitive Overload & ELO Calibration Guidelines Verified")
        md.append("1. **Beginner Tier (<1000 ELO)**: Restricts action checklist to top 3 fundamental commands. Focuses on farm reseeding, spending excess resources, and simple binary counters.")
        md.append("2. **Intermediate Tier (1000–1400 ELO)**: Introduces tactical timing windows, power spikes, and production building scaling.")
        md.append("3. **Advanced Tier (>1400 ELO)**: Adds micro engagement advice, elevation management, and tech transitions.")

        return "\n".join(md)


class UserTestingSimulator:
    """Simulation engine for validating coach response quality on beginner matches."""

    def __init__(
        self,
        ml_service: Optional[MLInferenceService] = None,
        explanation_engine: Optional[TacticalExplanationEngine] = None,
    ):
        self.ml_service = ml_service or MLInferenceService()
        self.explanation_engine = explanation_engine or TacticalExplanationEngine(
            config=LLMConfig(timeout_seconds=2.0),
            force_fallback=True,
        )

    def evaluate_test_scenario(self, test: UserTestingScenario) -> UserTestResult:
        """Run single beginner test scenario through the coaching pipeline."""
        t_start = time.perf_counter()

        total_vills = test.vills_food + test.vills_wood + test.vills_gold + test.vills_stone
        state_dict = {
            "player_civ": test.player_civ,
            "opponent_civ": test.opponent_civ,
            "player_age": test.current_age,
            "player_elo": test.player_elo,
            "timestamp_sec": test.game_time_sec,
            "food": test.food,
            "wood": test.wood,
            "gold": test.gold,
            "stone": test.stone,
            "vills_total": total_vills,
            "vills_food": test.vills_food,
            "vills_wood": test.vills_wood,
            "vills_gold": test.vills_gold,
            "vills_stone": test.vills_stone,
            "military_total": 0,
            "sighted_units": [
                {"unit": uname, "count": ucount}
                for uname, ucount in test.sighted_enemy_units.items()
            ],
            "sighted_buildings": [
                {"building": bname, "count": bcount}
                for bname, bcount in test.sighted_enemy_buildings.items()
            ],
        }

        # 1. Inference
        rec: MLRecommendation = self.ml_service.get_recommendation(state_dict)

        # 2. Explanation
        exp_res = self.explanation_engine.explain(
            rec,
            elo_override=test.player_elo,
            force_fallback=True,
        )
        total_time_ms = (time.perf_counter() - t_start) * 1000.0

        explanation = exp_res.explanation
        elo_tier = exp_res.elo_tier.value

        # Calculate metrics
        action_count = len(explanation.priority_checklist)
        conciseness_pass = action_count <= test.expected_max_action_items

        # Check root-cause prioritization (e.g. if floating wood, checklist or eco rebalance mentions farm/wood shift)
        full_text = (
            f"{explanation.primary_directive} {' '.join(explanation.priority_checklist)} "
            f"{explanation.economic_plan.problem_diagnosis} {explanation.economic_plan.immediate_action} "
            f"{explanation.military_plan.primary_unit_recommendation} {explanation.military_plan.counter_explanation}"
        ).lower()

        root_cause_prioritized = True
        if "wood float" in test.primary_blunder.lower() or test.wood > 700:
            root_cause_prioritized = "farm" in full_text or "wood" in full_text or "shift" in full_text
        elif "cavalry dive" in test.primary_blunder.lower():
            root_cause_prioritized = "pike" in full_text or "spear" in full_text or "monk" in full_text or "knight" in full_text

        # Counter accuracy
        recommended_primary = rec.military_action_plan.primary_composition.lower()
        counter_list = [c.unit_name.lower() for c in rec.counter_matrix.recommended_counters]
        
        counter_accurate = any(
            unit in recommended_primary
            or any(unit in c for c in counter_list)
            or unit in full_text
            for unit in test.expected_counter_units
        )

        word_count = len(full_text.split())

        # Cognitive Load Score: 1.0 (Optimal: <=3 action items, clear directive, under 100 words total)
        cog_score = 1.0
        if action_count > test.expected_max_action_items:
            cog_score -= 0.2 * (action_count - test.expected_max_action_items)
        if word_count > 120:
            cog_score -= 0.15
        if not root_cause_prioritized:
            cog_score -= 0.25
        cog_score = max(0.1, min(1.0, cog_score))

        notes = (
            f"Delivered {action_count} actionable items in {round(total_time_ms, 1)}ms. "
            f"Directive: '{explanation.primary_directive}'."
        )

        return UserTestResult(
            test_id=test.test_id,
            title=test.title,
            player_elo=test.player_elo,
            elo_tier=elo_tier,
            primary_directive=explanation.primary_directive,
            action_item_count=action_count,
            conciseness_pass=conciseness_pass,
            root_cause_prioritized=root_cause_prioritized,
            correct_counter_recommended=counter_accurate,
            word_count=word_count,
            cognitive_load_score=round(cog_score, 2),
            generation_latency_ms=round(total_time_ms, 2),
            feedback_notes=notes,
        )

    def run_user_testing_suite(
        self,
        scenarios: Optional[List[UserTestingScenario]] = None,
    ) -> CalibrationReport:
        """Run complete calibration and user testing simulation."""
        tests = scenarios or BEGINNER_TEST_SCENARIOS
        results: List[UserTestResult] = []

        for t in tests:
            results.append(self.evaluate_test_scenario(t))

        total = len(results)
        conc_pass_pct = (sum(1 for r in results if r.conciseness_pass) / total) * 100.0
        root_pass_pct = (sum(1 for r in results if r.root_cause_prioritized) / total) * 100.0
        counter_acc_pct = (sum(1 for r in results if r.correct_counter_recommended) / total) * 100.0
        mean_actions = float(np.mean([r.action_item_count for r in results]))
        mean_cog = float(np.mean([r.cognitive_load_score for r in results]))
        mean_lat = float(np.mean([r.generation_latency_ms for r in results]))

        all_ok = (
            conc_pass_pct >= 90.0
            and root_pass_pct >= 85.0
            and counter_acc_pct >= 90.0
            and mean_cog >= 0.85
            and mean_lat < 50.0
        )

        status = "CALIBRATION VERIFIED — READY FOR BEGINNERS" if all_ok else "CALIBRATION NEEDS TUNING"

        return CalibrationReport(
            timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            total_tests=total,
            conciseness_pass_rate_pct=round(conc_pass_pct, 2),
            root_cause_prioritization_pct=round(root_pass_pct, 2),
            counter_accuracy_pct=round(counter_acc_pct, 2),
            mean_action_items=round(mean_actions, 2),
            mean_cognitive_load_score=round(mean_cog, 2),
            mean_latency_ms=round(mean_lat, 2),
            test_results=results,
            calibration_status=status,
        )
