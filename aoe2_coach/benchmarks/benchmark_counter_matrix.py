"""
Benchmark script to measure execution speed of CounterMatrixEngine recommendations.
"""

import time
from typing import Dict
from aoe2_coach.rules.counter_matrix import CounterMatrixEngine
from aoe2_coach.schemas.game_constants import Age


def benchmark_counter_matrix(num_calls: int = 1000) -> Dict[str, float]:
    engine = CounterMatrixEngine()
    enemy_scenarios = [
        ({"knight": 10, "crossbowman": 5}, "britons", "franks", Age.CASTLE),
        ({"archer": 12, "skirmisher": 4}, "ethiopians", "byzantines", Age.FEUDAL),
        ({"paladin": 15, "halberdier": 10}, "franks", "goths", Age.IMPERIAL),
        ({"mangonel": 3, "crossbowman": 15}, "celts", "vikings", Age.CASTLE),
    ]

    start_time = time.perf_counter()
    for i in range(num_calls):
        scenario = enemy_scenarios[i % len(enemy_scenarios)]
        engine.recommend_counters(
            player_civ=scenario[2],
            player_age=scenario[3],
            enemy_units=scenario[0],
            enemy_civ=scenario[1],
        )
    total_time = time.perf_counter() - start_time

    avg_ms = (total_time / num_calls) * 1000.0
    calls_per_sec = num_calls / total_time

    print(f"Benchmark finished: {num_calls} calls in {total_time:.4f} seconds.")
    print(f"Average latency per call: {avg_ms:.4f} ms")
    print(f"Throughput: {calls_per_sec:.2f} calls/sec")

    return {
        "total_time_sec": total_time,
        "avg_ms": avg_ms,
        "calls_per_sec": calls_per_sec,
    }


if __name__ == "__main__":
    benchmark_counter_matrix(2000)
