"""
Unit & Integration Tests for Phase 6: Benchmarks, ELO Calibration, and User Testing.
"""

import pytest
from aoe2_coach.benchmarks.pro_datasets import CURATED_PRO_SCENARIOS, ProScenario
from aoe2_coach.benchmarks.benchmark_engine import BenchmarkEngine, BenchmarkReport
from aoe2_coach.benchmarks.user_testing_calibration import (
    UserTestingSimulator,
    CalibrationReport,
    BEGINNER_TEST_SCENARIOS,
    UserTestingScenario,
)
from aoe2_coach.models.inference_service import MLInferenceService
from aoe2_coach.explanation.engine import TacticalExplanationEngine
from aoe2_coach.explanation.schemas import ELOTier, get_elo_tier


@pytest.fixture
def benchmark_engine():
    return BenchmarkEngine()


@pytest.fixture
def user_testing_simulator():
    return UserTestingSimulator()


def test_pro_scenario_data_integrity():
    """Verify curated pro tournament scenarios are well-formed."""
    assert len(CURATED_PRO_SCENARIOS) >= 10
    for sc in CURATED_PRO_SCENARIOS:
        assert isinstance(sc, ProScenario)
        assert sc.player_civ != ""
        assert sc.opponent_civ != ""
        assert sc.current_age in (2, 3, 4)
        assert len(sc.expected_winning_compositions) >= 1
        assert sc.player_elo >= 1800


def test_pro_benchmark_execution_and_accuracy(benchmark_engine):
    """Run pro benchmark suite and verify accuracy & latency SLAs."""
    report: BenchmarkReport = benchmark_engine.run_benchmark(
        scenarios=CURATED_PRO_SCENARIOS[:5],
        iterations_per_scenario=2,
    )
    s = report.summary
    assert s.total_scenarios == 5
    assert s.top1_accuracy_pct >= 70.0
    assert s.top3_recall_pct >= 80.0
    assert s.counter_validity_pct >= 90.0
    assert s.ml_latency.p99_ms < 20.0  # Sub-20ms SLA check
    assert s.mean_eco_mae_vills <= 4.0


def test_benchmark_markdown_generation(benchmark_engine):
    """Verify Markdown report generation format."""
    report = benchmark_engine.run_benchmark(scenarios=CURATED_PRO_SCENARIOS[:3])
    md = report.to_markdown()
    assert "# AoE2 Coach AI — Pro Tournament Match Benchmark Report" in md
    assert "Top-1 Strategy Agreement" in md
    assert "ML ONNX Inference Engine" in md


def test_beginner_user_testing_scenarios():
    """Verify beginner crisis scenarios are structured correctly."""
    assert len(BEGINNER_TEST_SCENARIOS) >= 10
    for t in BEGINNER_TEST_SCENARIOS:
        assert isinstance(t, UserTestingScenario)
        assert 800 <= t.player_elo <= 1250
        assert len(t.expected_counter_units) >= 1
        assert t.expected_max_action_items in (3, 4)


def test_user_testing_calibration_suite(user_testing_simulator):
    """Run beginner user testing simulation and verify cognitive load reduction."""
    report: CalibrationReport = user_testing_simulator.run_user_testing_suite(BEGINNER_TEST_SCENARIOS)
    
    assert report.total_tests == len(BEGINNER_TEST_SCENARIOS)
    assert report.conciseness_pass_rate_pct >= 90.0
    assert report.root_cause_prioritization_pct >= 85.0
    assert report.counter_accuracy_pct >= 90.0
    assert report.mean_cognitive_load_score >= 0.85
    assert report.mean_latency_ms < 50.0
    assert "CALIBRATION VERIFIED" in report.calibration_status


def test_elo_tier_differentiation():
    """Verify ELO-calibrated explanation filtering."""
    assert get_elo_tier(850) == ELOTier.BEGINNER
    assert get_elo_tier(1200) == ELOTier.INTERMEDIATE
    assert get_elo_tier(1600) == ELOTier.ADVANCED
