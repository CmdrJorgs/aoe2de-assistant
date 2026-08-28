# Age of Empires II: DE — Real-Time Tactical & Strategic AI Coach

[![CI](https://img.shields.io/badge/tests-38%20passed-brightgreen.svg)](aoe2_coach/tests)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](pyproject.toml)
[![Package Manager](https://img.shields.io/badge/uv-supported-blueviolet.svg)](https://github.com/astral-sh/uv)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An intelligent, real-time tactical and strategic decision-support system designed for *Age of Empires II: Definitive Edition* players. 

AoE2 Coach solves the mid-match cognitive overload of RTS gameplay by combining:
1. **Fog-of-War Replay Data Mining**: Ingests high-ELO competitive replays and simulates partial observability / scouting memory.
2. **Deterministic AoE2 Domain Rules Engine**: Encodes all 45+ civilizations, unique technologies, armor classes, damage formulas, and counter matrices.
3. **Linear Programming Economy Solver**: Calculates exact villager distributions (Food, Wood, Gold, Stone) to sustain military production with zero wasted idle time.
4. **Machine Learning & ELO-Calibrated Coaching**: Delivers prioritized, actionable advice tailored to player rating brackets.

---

## 🏛️ System Architecture

```
                      +---------------------------------------+
                      |         USER / CLIENT SNAPSHOT        |
                      |  - Civ Matchup & ELO                  |
                      |  - Game Time & Stockpile              |
                      |  - Sighted Enemy Units & Buildings    |
                      +-------------------+-------------------+
                                          |
                                          v
+-----------------------------------------------------------------------------------+
|                              AOE2 COACH CORE ENGINE                               |
|                                                                                   |
|  +------------------------------+             +--------------------------------+  |
|  |     DOMAIN RULES ENGINE      |             |         ECONOMY SOLVER         |  |
|  |  - 45+ Civ Tech Trees        |             |  - Villager Allocation Matrix  |  |
|  |  - Damage & Armor Class Calc |             |  - Eco Tech Upgrades Modifier  |  |
|  |  - Counter Matrix Generator  |             |  - Gather vs Distance Penalties|  |
|  +--------------+---------------+             +---------------+----------------+  |
|                 |                                             |                   |
|                 +-----------------------+---------------------+                   |
|                                         |                                         |
|                                         v                                         |
|  +-----------------------------------------------------------------------------+  |
|  |                    STRATEGY & COUNTER RECOMMENDATION                        |  |
|  |  - Cost-Effective Unit Counters & Compositions                             |  |
|  |  - Production Building Targets & Tech Timings                               |  |
|  +--------------------------------------+--------------------------------------+  |
+-----------------------------------------|-----------------------------------------+
                                          v
                      +---------------------------------------+
                      |       ACTIONABLE COACHING OUTPUT      |
                      |  1. Recommended Army Composition      |
                      |  2. Precise Villager Balance Targets  |
                      |  3. Strategic Stance & Timing Windows |
                      +---------------------------------------+
```

---

## ✨ Key Features

### 1. Complete AoE2:DE Domain Knowledge & Damage Engine
- **Armor Classes**: Full modeling of pierce, melee, cavalry, archer, infantry, siege, spearman, camel, unique ships, and elephant armor classes.
- **Damage Formula**: Accurate AoE2 damage calculation including base attack, armor subtractions, positive and negative class bonuses, hill advantage ($\pm 25\%$), and attack accuracy with dispersion.
- **Counter Matrix**: Dynamic calculation of combat outcome ratings, cost efficiency (resources traded per second), and tech-tree availability for all 45+ civilizations.

### 2. Macro Economy & Villager Allocation Solver
- **Dynamic Gather Rates**: Calibrated baseline gather speeds across Sheep, Berries, Farms, Woodlines, Gold, and Stone.
- **Eco Upgrades**: Accurate multiplier stacking for Wheelbarrow, Hand Cart, Double-Bit Axe, Bow Saw, Two-Man Saw, Gold Mining, Gold Shaft Mining, and civ-specific bonuses.
- **Production Balancer**: Computes exact villager allocations required to sustain continuous queues for any target military composition and tech research goals without resource bottlenecks.

### 3. Replay Parser & Fog-of-War Pipeline
- **Binary Parser**: High-performance replay extraction powered by `aoe2rec-py` and `mgz`.
- **Partial Observability**: Simulates realistic player line-of-sight and scouting memory decay so training data accurately reflects what a live player knows.
- **Parquet & DuckDB Mining**: Batch extracts 5-minute snapshot vectors into columnar Parquet format for machine learning workflows.

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`

### Installation

```bash
# Clone the repository
git clone https://github.com/CmdrJorgs/aoe2de-assistant.git
cd aoe2de-assistant

# Install dependencies using uv
uv sync
```

Or with `pip`:
```bash
pip install -e .
```

### Running Tests

```bash
uv run pytest
```

---

## 💡 Code Examples

### 1. Calculate Combat Damage & Battle Matchups

```python
from aoe2_coach.rules.damage_calculator import (
    calculate_damage,
    simulate_battle,
    CombatantState,
)
from aoe2_coach.rules.units import KNIGHT, PIKEMAN

# Calculate single-hit damage from a Pikeman to a Knight
damage = calculate_damage(
    attacker=PIKEMAN,
    defender=KNIGHT,
    attacker_elevation=0,
    defender_elevation=0,
)
print(f"Pikeman damage against Knight: {damage.total_damage} HP")
# Output: Pikeman damage against Knight: 26 HP (4 base - 2 armor + 22 bonus vs cavalry + 2 bonus vs war elephant)

# Simulate 1v1 battle
outcome = simulate_battle(
    unit_a=PIKEMAN,
    unit_b=KNIGHT,
)
print(f"Winner: {outcome.winner} (TTK: {outcome.time_to_kill_a_vs_b:.1f}s vs {outcome.time_to_kill_b_vs_a:.1f}s)")
```

### 2. Generate Counter-Unit Recommendations

```python
from aoe2_coach.rules.counter_matrix import CounterMatrixEngine
from aoe2_coach.schemas.game_constants import Age, Civilization

engine = CounterMatrixEngine()

# Find the best counters against Franks Paladins in Imperial Age for Britons
counters = engine.recommend_counter_composition(
    enemy_army={"Paladin": 15},
    player_civ=Civilization.BRITONS,
    current_age=Age.IMPERIAL,
    budget_weight="cost_efficiency",
)

for rec in counters:
    print(f"Counter: {rec.unit.name} | Score: {rec.score:.2f} | Reason: {rec.reasoning}")
```

### 3. Calculate Required Villager Economy for Army Production

```python
from aoe2_coach.rules.economy_solver import EconomySolver
from aoe2_coach.schemas.game_constants import Age, Civilization

solver = EconomySolver()

# Calculate villagers needed to continuously produce Crossbowmen from 2 Archery Ranges
# while sustaining 1 Town Center making villagers in Castle Age
plan = solver.calculate_villagers_for_production(
    production_goals=[
        {"unit_name": "Crossbowman", "building_count": 2},
        {"unit_name": "Villager", "building_count": 1},
    ],
    researched_upgrades=["Wheelbarrow", "Double-Bit Axe", "Bow Saw", "Gold Mining"],
    civ=Civilization.BRITONS,
    current_age=Age.CASTLE,
)

print(f"Target Villagers: Food: {plan.food_vills}, Wood: {plan.wood_vills}, Gold: {plan.gold_vills}, Stone: {plan.stone_vills}")
print(f"Total Eco Count: {plan.total_vills} villagers")
```

---

## 📁 Repository Structure

```
aoe2-coach/
├── aoe2_coach/
│   ├── pipeline/               # Replay Harvester, Parser, FoW Simulator, Parquet Exporter
│   │   ├── dataset_exporter.py # Columnar Parquet dataset generator
│   │   ├── fog_of_war.py       # Player vision & scouting memory simulation
│   │   ├── harvester.py        # Automated replay scraping & download client
│   │   ├── parser.py           # .aoe2record binary parser
│   │   ├── simulator.py        # Replay event simulation
│   │   └── snapshot_extractor.py # State vector extraction
│   ├── rules/                  # AoE2:DE Deterministic Domain Knowledge
│   │   ├── armor_classes.py    # Game armor classes & damage types
│   │   ├── counter_matrix.py   # Unit counter scoring & composition recommendations
│   │   ├── damage_calculator.py# Melee, Pierce, Bonus & Elevation damage engine
│   │   ├── economy_solver.py   # Villager gather rates & production balance solver
│   │   ├── tech_tree.py        # 45+ Civilization tech availability & unique tech rules
│   │   └── units.py            # Unit statistics database
│   ├── schemas/                # Data structures & Pydantic models
│   │   ├── game_constants.py   # Ages, Civilizations, Resource Types
│   │   └── match.py            # Snapshot & Replay state models
│   └── tests/                  # Pytest test suite (38 unit & integration tests)
├── scripts/                    # CLI runner scripts
│   ├── parse_sample_replay.py  # Inspect sample .aoe2record files
│   ├── run_harvest.py          # Run replay crawler
│   └── run_pipeline.py         # Batch export replay snapshots
├── PROJECT_PLAN.md             # Complete 6-phase engineering specification
├── pyproject.toml              # Project metadata & dependencies
└── README.md                   # Project overview & documentation
```

---

## 🗺️ Roadmap

- [x] **Phase 1: Replay Pipeline, Fog of War, & Dataset Mining**
  - Binary parsing of `.aoe2record` files
  - Line-of-sight tracking and scouting decay memory
  - High-performance Parquet time-slice vector extraction
- [x] **Phase 2: Domain Rules & Counter-Matrix Engine**
  - Complete 45+ civilization tech trees and unit stats
  - Multi-class damage formula with hill advantage and accuracy
  - Linear villager macro-economy solver
- [x] **Phase 3: Machine Learning Model Development**
  - Win-rate and strategic action predictor models (ONNX sub-20ms)
  - Economic rebalancer and stance/timing classifiers
- [x] **Phase 4: LLM Coaching & Explanation Layer**
  - Local CPU llama.cpp inference with Qwen3.8-4B-Distill-GGUF
  - ELO-adaptive verified coaching generation with deterministic fallback
- [x] **Phase 5: Real-Time Web Application & FastAPI Gateway**
  - Next.js 15 App with RTS high-contrast dark mode styling
  - 30-Second Match & Mid-game Entry Wizard with visual icon pickers
  - Real-time speech / voice-to-text input parsing
  - Interactive Tactical Dashboard with gatherer redistribution & combat simulator
- [ ] **Phase 6: ELO Calibration & Beta Testing**

---

### 🌐 Starting the Application

#### 1. Start the FastAPI Backend Gateway
```bash
uv run python scripts/start_api_server.py --port 8000
```

#### 2. Start the Next.js Frontend
```bash
cd frontend
npm run dev
```
Navigate to `http://localhost:3000` to use the AoE2 Coach Web Application.

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

*Age of Empires II: Definitive Edition* is a registered trademark of Microsoft Corporation. This project is a community-developed AI coaching tool and is not affiliated with or endorsed by Microsoft or World's Edge.
