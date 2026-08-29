"""
AoE2 Coach Benchmarking and Evaluation Package (Phase 6).
Provides tools to benchmark ML models and rules against pro tournament matches,
evaluate ELO calibration, and simulate user testing with beginner players.
"""

from aoe2_coach.benchmarks.pro_datasets import (
    ProScenario,
    CURATED_PRO_SCENARIOS,
    load_parquet_pro_snapshots,
)
from aoe2_coach.benchmarks.benchmark_engine import (
    BenchmarkEngine,
    BenchmarkResult,
    BenchmarkReport,
)
from aoe2_coach.benchmarks.user_testing_calibration import (
    UserTestingSimulator,
    UserTestingScenario,
    CalibrationReport,
)

__all__ = [
    "ProScenario",
    "CURATED_PRO_SCENARIOS",
    "load_parquet_pro_snapshots",
    "BenchmarkEngine",
    "BenchmarkResult",
    "BenchmarkReport",
    "UserTestingSimulator",
    "UserTestingScenario",
    "CalibrationReport",
]
