# Age of Empires II: DE — Real-Time Tactical & Strategic AI Coach

[![CI](https://img.shields.io/badge/tests-95%20passed-brightgreen.svg)](aoe2_coach/tests)
[![Python](https://img.shields.io/badge/python-3.11%20%7C%203.12-blue.svg)](pyproject.toml)
[![Next.js](https://img.shields.io/badge/Next.js-15.5-black.svg)](frontend/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20P99-<2ms-informational.svg)](models/artifacts)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)](Dockerfile)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Kustomize-326CE5.svg)](k8s/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An intelligent, real-time tactical and strategic decision-support system designed for *Age of Empires II: Definitive Edition* players. 

AoE2 Coach solves the mid-match cognitive overload of RTS gameplay by combining:
1. **Fog-of-War Replay Mining**: Ingests high-ELO competitive replays and simulates partial observability / scouting memory decay.
2. **Deterministic AoE2 Domain Rules Engine**: Encodes all 45+ civilizations, unique technologies, armor classes, damage formulas, and counter matrices.
3. **Linear Programming Economy Solver**: Calculates exact villager distributions (Food, Wood, Gold, Stone) to sustain military production with zero wasted idle time.
4. **Machine Learning & ONNX Inference (<2ms P99)**: Delivers instant strategic composition, economic rebalancing, tactical stance, and win probability predictions.
5. **Verified Tactical Explainer & ELO Calibrator**: Delivers ELO-tailored action items with a deterministic sub-millisecond fallback engine.
6. **Multi-Target Cloud Deployment**: Containerized for Kubernetes, Google Cloud Run, Docker Compose, and Vercel/Cloudflare edge CDN.

---

## 🏛️ System Architecture

```
                                  +---------------------------+
                                  |      GLOBAL USERS         |
                                  +-------------+-------------+
                                                |
                                                v
                   +---------------------------------------------------------+
                   |           CLOUDFLARE CDN / VERCEL EDGE NETWORK          |
                   |   - Static Asset Caching (HTML, CSS, JS, AoE2 Icons)    |
                   |   - Direct Route: "/" -> Next.js 15 Standalone UI       |
                   |   - Proxy Route:  "/api/*" -> FastAPI Gateway           |
                   +----------------------------+----------------------------+
                                                |
                                                v
                   +---------------------------------------------------------+
                   |                PRODUCTION BACKEND RUNTIME               |
                   |      (Kubernetes / Google Cloud Run / Docker Cluster)   |
                   |                                                         |
                   |  +---------------------------------------------------+  |
                   |  |          FastAPI API Gateway (Gunicorn/Uvicorn)   |  |
                   |  +-------------------------+-------------------------+  |
                   |                            |                            |
                   |        +-------------------+-------------------+        |
                   |        |                                       |        |
                   |        v                                       v        |
                   |  +-------------------+                   +-----------+  |
                   |  | ONNX Inference    |                   | Rules &   |  |
                   |  | Engine (<2ms P99) |                   | Counters  |  |
                   |  +---------+---------+                   +-----+-----+  |
                   |            |                                   |        |
                   |            +-----------------+-----------------+        |
                   |                              |                          |
                   |                              v                          |
                   |  +---------------------------------------------------+  |
                   |  | Verified Tactical Explainer & ELO Calibrator     |  |
                   |  | (Deterministic Fallback <1ms | LLM Endpoint)     |  |
                   |  +---------------------------------------------------+  |
                   +---------------------------------------------------------+
```

---

## ✨ Key Capabilities

### 1. Complete AoE2:DE Domain Knowledge & Damage Engine
- **Armor Classes**: Full modeling of pierce, melee, cavalry, archer, infantry, siege, spearman, camel, unique ships, and elephant armor classes.
- **Damage Formula**: Accurate AoE2 damage calculation including base attack, armor subtractions, positive and negative class bonuses, hill advantage ($\pm 25\%$), and attack accuracy with dispersion.
- **Counter Matrix**: Dynamic calculation of combat outcome ratings, cost efficiency (resources traded per second), and tech-tree availability for all 45+ civilizations.

### 2. Macro Economy & Villager Allocation Solver
- **Dynamic Gather Rates**: Calibrated baseline gather speeds across Sheep, Berries, Farms, Woodlines, Gold, and Stone.
- **Eco Upgrades**: Accurate multiplier stacking for Wheelbarrow, Hand Cart, Double-Bit Axe, Bow Saw, Two-Man Saw, Gold Mining, Gold Shaft Mining, and civ-specific bonuses.
- **Production Balancer**: Computes exact villager allocations required to sustain continuous queues for any target military composition and tech research goals without resource bottlenecks.

### 3. ML Inference Engine (<2ms P99 Latency)
- **Strategy Classifier**: Predicts optimal unit compositions across 10 strategic classes (Knights, Crossbows, Monks, Pikes, Camels, Siege, Unique Units, Skirms, Scouts, Champions).
- **Economic Rebalancer**: Multi-target regression predicting exact villager shifts and macro leak severity.
- **Stance & Timing**: Predicts tactical postures (`FORWARD_PRESSURE`, `ALL_IN_AGGRESSION`, `DEFENSIVE_TURTLING`, `RELIC_HILL_CONTROL`, `FAST_IMPERIAL_BOOM`) and attack timing windows.
- **Win Probability Estimator**: Calibrated logistic win predictor based on economic stockpiles and military count differentials.

### 4. Verified Tactical Explainer & ELO Calibration
- **Tier Calibration**: Calibrates actionable guidance specifically for Beginner (<1000 ELO), Intermediate (1000–1400 ELO), and Advanced (>1400 ELO) players.
- **Cognitive Load Reduction**: Low-ELO recommendations are strictly limited to $\le 3$ high-impact action items with plain-English macro directives.
- **Deterministic Zero-Latency Fallback**: High-reliability fallback engine guarantees instant (<1ms) response with 0% tech tree hallucinations even if LLM endpoints are unavailable.

### 5. Dynamic Asset Database & Icon System
- **Comprehensive Coverage**: 10,987 total mappings across all **59 civilizations** + global fallback catalog (`_all`) covering base units, unique units, campaign heroes, buildings, and technologies.
- **Automated DDS to PNG Conversion**: Automated conversion and cleanup pipeline with `RGBA` transparency optimization.
- **Dual-Storage Formats**: High-speed zero-dependency JSON (`assets_db.json`) for client-side web loading alongside indexed SQLite (`aoe2_assets.db`) for structured backend queries.

---

## 🎨 Dynamic Asset Database

The project includes an optimized, multi-format asset database and automated pipeline that powers dynamic in-game icon retrieval across **all 59 civilizations** (Definitive Edition, Return of Rome, DLCs, and scenario assets).

### Database Schema

```json
{
  "<civilization_name>": {
    "unit": {
      "<unit_key>": {
        "name": "<Display Name>",
        "image": "/aoe2_assets/units/<filename>.png",
        "available": true,
        "age_id": 1,
        "picture_index": 17
      }
    },
    "building": {
      "<building_key>": {
        "name": "<Display Name>",
        "image": "/aoe2_assets/buildings/<filename>.png",
        "available": true,
        "age_id": 2,
        "picture_index": 0
      }
    },
    "tech": {
      "<tech_key>": {
        "name": "<Display Name>",
        "image": "/aoe2_assets/tech/<filename>.png",
        "available": true,
        "age_id": 1,
        "picture_index": 6
      }
    }
  }
}
```

### Generated Database Artifacts

| Format | Path | Purpose |
| :--- | :--- | :--- |
| **JSON** (Frontend) | `frontend/public/aoe2_assets/assets_db.json` | High-speed browser fetch & dynamic UI rendering with zero dependencies |
| **SQLite** (Frontend) | `frontend/public/aoe2_assets/aoe2_assets.db` | Indexed SQLite database (10,987 rows) |
| **JSON** (Backend) | `aoe2_coach/data/assets_db.json` | Local cache for backend API & explanation services |
| **SQLite** (Backend) | `aoe2_coach/data/aoe2_assets.db` | Relational query store for Python services |

### Usage Examples

**Frontend (TypeScript / Next.js)**:
```typescript
import {
  getAssetDatabase,
  getUnitImageUrl,
  getBuildingImageUrl,
  getTechImageUrl,
  isCivAssetAvailable,
} from "@/lib/assetDb";

// Load/cache database
const db = await getAssetDatabase();

// Dynamic icon lookups
const knightImg = getUnitImageUrl(db, "knight", "franks");     // "/aoe2_assets/units/001_knight.png"
const castleImg = getBuildingImageUrl(db, "castle", "franks"); // "/aoe2_assets/buildings/007_castle.png"
const loomImg = getTechImageUrl(db, "loom", "franks");         // "/aoe2_assets/tech/006_loom.png"

// Tech-tree availability check
const hasPaladin = isCivAssetAvailable(db, "paladin", "franks"); // true
```

**Backend (Python)**:
```python
from aoe2_coach.rules.asset_db import default_asset_db

# Direct lookup
knight_img = default_asset_db.get_unit_image("knight", civ="franks")

# SQL relational queries
available_units = default_asset_db.query_sqlite(civ="franks", category="unit", available_only=True)
```

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+**
- [`uv`](https://github.com/astral-sh/uv) (recommended) or `pip`
- **Node.js 20+** (for frontend)

### Installation

```bash
# Clone the repository
git clone https://github.com/CmdrJorgs/aoe2de-assistant.git
cd aoe2de-assistant

# Install dependencies using uv
uv sync
```

### Running Tests
```bash
uv run pytest
```

### Running Pro Tournament Benchmarks & User Testing Simulations
```bash
# 1. Pro tournament match benchmark (15 curated pro situations)
uv run python scripts/benchmark_pro_matches.py --iterations 10

# 2. 800-1200 ELO beginner crisis user testing simulation (12 live crisis scenarios)
uv run python scripts/run_user_testing_simulation.py
```

### Rebuilding Asset Databases
```bash
# Rebuild JSON and SQLite asset catalogs
uv run python scripts/build_asset_database.py
```

---

## 🐳 Containerized & Cloud Deployment

### 1. Local Multi-Container Stack (Docker Compose)
```bash
# Start backend API (8000) and Next.js frontend (3000)
docker compose up -d --build
```

### 2. Kubernetes Deployment (Kustomize)
```bash
kubectl apply -k k8s/
```

### 3. Google Cloud Run Automated Deployment
```bash
chmod +x deploy/cloudrun/deploy.sh
./deploy/cloudrun/deploy.sh
```

### 4. Vercel & Cloudflare Edge Deployment
See [DEPLOYMENT.md](DEPLOYMENT.md) for full cloud configuration and environment variables.

---

## 📁 Repository Structure

```
aoe2-coach/
├── aoe2_coach/
│   ├── api/                    # FastAPI REST & WebSocket server, Gunicorn config
│   │   ├── app.py              # Application factory & routes
│   │   ├── gunicorn_conf.py    # Production Gunicorn worker settings
│   │   ├── routes.py           # /api/recommend, /api/combat, /api/health
│   │   ├── service.py          # API gateway orchestrator
│   │   └── voice_parser.py     # Natural language match state parser
│   ├── benchmarks/             # Phase 6 Evaluation & Simulation Suites
│   │   ├── benchmark_engine.py # Pro tournament match benchmarking
│   │   ├── pro_datasets.py     # 15 curated high-ELO pro match scenarios
│   │   └── user_testing_calibration.py # 12 beginner live crisis scenarios
│   ├── data/                   # Compiled backend asset databases (JSON & SQLite)
│   │   ├── aoe2_assets.db      # Indexed SQLite database
│   │   └── assets_db.json      # Structured JSON database
│   ├── explanation/            # Tactical Coaching & LLM Layer
│   │   ├── client.py           # OpenAI-compatible API client
│   │   ├── engine.py           # Verified explanation engine orchestrator
│   │   ├── fallback_engine.py  # Deterministic ELO-calibrated fallback (<1ms)
│   │   ├── prompts.py          # ELO-specific prompt builder
│   │   ├── schemas.py          # Coaching explanation Pydantic schemas
│   │   └── verifier.py         # Tech-tree & counter matrix hallucination checker
│   ├── models/                 # Machine Learning & ONNX Inference
│   │   ├── economic_rebalancer.py # Villager reallocation regressor
│   │   ├── feature_encoder.py  # 24-dimensional feature vectorizer
│   │   ├── inference_service.py# Unified ML inference orchestrator
│   │   ├── onnx_inference.py   # High-throughput ONNX Runtime sessions
│   │   ├── stance_timing_predictor.py # Tactical posture classifier
│   │   ├── strategy_classifier.py # 10-class composition classifier
│   │   └── win_probability_estimator.py # Match advantage estimator
│   ├── pipeline/               # Replay Harvester, Parser, FoW Simulator, Parquet Exporter
│   │   ├── dataset_exporter.py # Columnar Parquet dataset generator
│   │   ├── fog_of_war.py       # Player vision & scouting memory simulation
│   │   ├── harvester.py        # Automated replay scraping & download client
│   │   ├── parser.py           # .aoe2record binary parser
│   │   ├── simulator.py        # Replay event simulation
│   │   └── snapshot_extractor.py # State vector extraction
│   ├── rules/                  # AoE2:DE Deterministic Domain Knowledge
│   │   ├── armor_classes.py    # Game armor classes & damage types
│   │   ├── asset_db.py         # Dynamic asset & image querying client
│   │   ├── counter_matrix.py   # Unit counter scoring & composition recommendations
│   │   ├── damage_calculator.py# Melee, Pierce, Bonus & Elevation damage engine
│   │   ├── economy_solver.py   # Villager gather rates & production balance solver
│   │   ├── tech_tree.py        # 45+ Civilization tech availability & unique tech rules
│   │   └── units.py            # Unit statistics database
│   ├── schemas/                # Data structures & Pydantic models
│   │   ├── game_constants.py   # Ages, Civilizations, Resource Types
│   │   └── match.py            # Snapshot & Replay state models
│   └── tests/                  # Pytest test suite (95 unit & integration tests)
├── deploy/                     # Cloud Run and serverless deployment manifests
│   └── cloudrun/
├── frontend/                   # Next.js 15 Tailwind UI Application
│   ├── app/                    # App router pages & layouts
│   ├── components/             # Tactical dashboard, match wizard, voice input
│   ├── lib/                    # API client, audio transcription & assetDb client
│   ├── public/aoe2_assets/     # Processed PNG assets & web database
│   │   ├── aoe2_assets.db      # SQLite asset database
│   │   ├── assets_db.json      # JSON asset database
│   │   ├── buildings/          # 107 PNG building icons
│   │   ├── CivTechTrees/       # 59 Civilization JSON tech tree definitions
│   │   ├── tech/               # 304 PNG technology icons
│   │   └── units/              # 755 PNG unit icons
│   ├── Dockerfile              # Next.js standalone container
│   ├── vercel.json             # Vercel edge proxy configuration
│   └── wrangler.toml           # Cloudflare Pages configuration
├── k8s/                        # Production Kubernetes manifests (Kustomize)
├── models/artifacts/           # Trained ONNX model binaries (.onnx) & scaler
├── scripts/                    # CLI runner & conversion scripts
│   ├── build_asset_database.py # JSON & SQLite database compiler
│   ├── convert_and_rename_units.py # Initial unit icon converter
│   ├── convert_assets_to_png.py # Generic DDS -> PNG batch converter
│   └── rename_units_from_civ_tech_trees.py # CivTechTrees metadata renamer
├── Dockerfile                  # Production multi-stage backend container
├── docker-compose.yml          # Local development stack
├── docker-compose.prod.yml     # Production Docker stack
├── DEPLOYMENT.md               # Complete production deployment & operations guide
├── PROJECT_PLAN.md             # 6-phase engineering specification
└── README.md                   # Project overview & documentation
```

---

## 🗺️ Roadmap & Project Status

- [x] **Phase 1: Replay Pipeline, Fog of War, & Dataset Mining**
  - Binary parsing of `.aoe2record` files (`aoe2rec-py`, `mgz`)
  - Line-of-sight tracking and scouting decay memory
  - High-performance Parquet time-slice vector extraction
- [x] **Phase 2: Domain Rules & Counter-Matrix Engine**
  - Complete 45+ civilization tech trees and unit statistics
  - Multi-class damage formula with hill advantage and accuracy
  - Linear villager macro-economy solver
- [x] **Phase 3: Machine Learning Model Development**
  - Strategy composition, economic rebalancer, stance timing, and win probability models
  - ONNX export and ultra-low latency inference (<2ms P99)
- [x] **Phase 4: LLM Coaching & Explanation Layer**
  - ELO-adaptive coaching with strict hallucination verification
  - Deterministic zero-latency fallback engine
- [x] **Phase 5: Real-Time Web Application & FastAPI Gateway**
  - Next.js 15 App with RTS dark mode styling
  - 30-Second Match & Mid-game Entry Wizard with visual icon pickers
  - Real-time voice-to-text / speech input parsing
  - Interactive Tactical Dashboard with gatherer redistribution & combat simulator
- [x] **Phase 6: Testing, Calibration & Deployment**
  - Pro tournament match benchmarking suite (86.7% Top-1, 93.3% Top-3 Recall, 100% Counter Matrix compliance)
  - 800–1200 ELO beginner crisis simulation & cognitive load calibration (100% Action Item Limit pass, 100% Root-Cause prioritization)
  - Production multi-stage Dockerfiles, Docker Compose, Kubernetes manifests, Cloud Run scripts, and CI/CD pipelines

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

*Age of Empires II: Definitive Edition* is a registered trademark of Microsoft Corporation. This project is a community-developed AI coaching tool and is not affiliated with or endorsed by Microsoft or World's Edge.
