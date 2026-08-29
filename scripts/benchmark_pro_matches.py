#!/usr/bin/env python3
"""
AoE2 Coach — Pro Tournament Match Benchmark CLI (Phase 6).
Benchmarks ML ONNX models and rules engine against top-tier pro match scenarios.
"""

import sys
import os
import argparse
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aoe2_coach.benchmarks.benchmark_engine import BenchmarkEngine, BenchmarkReport
from aoe2_coach.benchmarks.pro_datasets import CURATED_PRO_SCENARIOS


def main():
    parser = argparse.ArgumentParser(description="Run AoE2 Coach Pro Tournament Benchmark Suite")
    parser.add_argument("--iterations", type=int, default=1, help="Latency iterations per scenario")
    parser.add_argument("--export-json", type=str, default="benchmark_report.json", help="Path to export JSON report")
    parser.add_argument("--export-md", type=str, default="BENCHMARK_REPORT.md", help="Path to export Markdown report")
    parser.add_argument("--quiet", action="store_true", help="Suppress verbose console output")
    args = parser.parse_args()

    print("================================================================================")
    print("           AoE2 COACH AI — PRO TOURNAMENT MATCH BENCHMARK SUITE                 ")
    print("================================================================================")
    print(f"[*] Total Scenarios: {len(CURATED_PRO_SCENARIOS)}")
    print(f"[*] Profiling Iterations per Scenario: {args.iterations}")
    print("[*] Initializing ML ONNX Inference Engine & Rules Engine...")

    engine = BenchmarkEngine()
    print("[*] Executing Pro Benchmark Evaluation...")

    report: BenchmarkReport = engine.run_benchmark(
        scenarios=CURATED_PRO_SCENARIOS,
        iterations_per_scenario=args.iterations,
    )

    # Print summary to console
    s = report.summary
    print("\n" + "=" * 80)
    print("                             BENCHMARK RESULTS                                  ")
    print("=" * 80)
    print(f"• Top-1 Strategy Agreement:       {s.top1_accuracy_pct:.1f}%  (Target >= 75%)")
    print(f"• Top-3 Strategy Recall:          {s.top3_recall_pct:.1f}%  (Target >= 90%)")
    print(f"• Production Building Match:      {s.building_accuracy_pct:.1f}%  (Target >= 80%)")
    print(f"• Tactical Stance Agreement:      {s.stance_agreement_pct:.1f}%  (Target >= 70%)")
    print(f"• Counter Matrix Compliance:      {s.counter_validity_pct:.1f}%  (Target >= 90%)")
    print(f"• Macro Rebalance MAE:            {s.mean_eco_mae_vills:.2f} villagers (Target <= 3.5)")
    print(f"• ML Inference P99 Latency:       {s.ml_latency.p99_ms:.2f} ms  (Target < 20ms)")
    print(f"• Total Pipeline P99 Latency:     {s.total_latency.p99_ms:.2f} ms")
    print("-" * 80)
    print(f"• Feudal Accuracy:                {s.feudal_top1_acc_pct:.1f}%")
    print(f"• Castle Accuracy:                {s.castle_top1_acc_pct:.1f}%")
    print(f"• Imperial Accuracy:              {s.imperial_top1_acc_pct:.1f}%")
    print("=" * 80)

    if s.all_slas_passed:
        print("\n>>> ALL QUALITY GATES & LATENCY SLAS PASSED (READY FOR DEPLOYMENT) <<<\n")
    else:
        print("\n>>> WARNING: SOME BENCHMARK GATES FAILED <<< \n")

    # Export JSON
    if args.export_json:
        with open(args.export_json, "w") as f:
            json.dump(report.model_dump(), f, indent=2)
        print(f"[✓] Exported JSON report to: {args.export_json}")

    # Export Markdown
    if args.export_md:
        with open(args.export_md, "w") as f:
            f.write(report.to_markdown())
        print(f"[✓] Exported Markdown report to: {args.export_md}")


if __name__ == "__main__":
    main()
