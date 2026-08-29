#!/usr/bin/env python3
"""
AoE2 Coach — 800–1200 ELO User Testing & Calibration Simulation CLI (Phase 6).
Evaluates coach recommendations against common beginner and intermediate match crises.
"""

import sys
import os
import argparse
import json

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from aoe2_coach.benchmarks.user_testing_calibration import (
    UserTestingSimulator,
    CalibrationReport,
    BEGINNER_TEST_SCENARIOS,
)


def main():
    parser = argparse.ArgumentParser(description="Run 800–1200 ELO User Testing Simulation & Calibration")
    parser.add_argument("--export-json", type=str, default="calibration_report.json", help="Path to export JSON report")
    parser.add_argument("--export-md", type=str, default="USER_TESTING_REPORT.md", help="Path to export Markdown report")
    args = parser.parse_args()

    print("================================================================================")
    print("      AoE2 COACH AI — 800–1200 ELO USER TESTING & CALIBRATION SIMULATION        ")
    print("================================================================================")
    print(f"[*] Testing {len(BEGINNER_TEST_SCENARIOS)} realistic beginner match crisis scenarios...")

    simulator = UserTestingSimulator()
    report: CalibrationReport = simulator.run_user_testing_suite(BEGINNER_TEST_SCENARIOS)

    print("\n" + "=" * 80)
    print("                            CALIBRATION RESULTS                                 ")
    print("=" * 80)
    print(f"• Action Item Limit Pass Rate:     {report.conciseness_pass_rate_pct:.1f}%  (Target >= 90%)")
    print(f"• Macro Root-Cause Prioritized:    {report.root_cause_prioritization_pct:.1f}%  (Target >= 85%)")
    print(f"• Beginner Counter Accuracy:       {report.counter_accuracy_pct:.1f}%  (Target >= 90%)")
    print(f"• Mean Action Items Delivered:     {report.mean_action_items:.1f} items (Max 3-4)")
    print(f"• Mean Cognitive Load Index:       {report.mean_cognitive_load_score:.2f} / 1.0 (Target >= 0.85)")
    print(f"• Mean Advice Generation Latency:  {report.mean_latency_ms:.2f} ms (Target < 50ms)")
    print("-" * 80)
    print(f"• Overall Status: {report.calibration_status}")
    print("=" * 80)

    if args.export_json:
        with open(args.export_json, "w") as f:
            json.dump(report.model_dump(), f, indent=2)
        print(f"[✓] Exported JSON report to: {args.export_json}")

    if args.export_md:
        with open(args.export_md, "w") as f:
            f.write(report.to_markdown())
        print(f"[✓] Exported Markdown report to: {args.export_md}")


if __name__ == "__main__":
    main()
