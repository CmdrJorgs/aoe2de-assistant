# Age of Empires II: DE — AI Mid-Game Tactical & Strategic Coach
## Comprehensive System Design & Engineering Blueprint

---

## Executive Summary & Vision

**AoE2 Coach** is an interactive, real-time decision-support web application designed to help beginner and intermediate *Age of Empires II: Definitive Edition* players make optimal tactical and strategic decisions mid-match. 

In RTS games, new players frequently struggle with cognitive overload: balancing macroeconomics (villager allocation, resource spending) with scouting interpretation (reading enemy unit transitions) and strategic planning (counter-compositions, timing windows). **AoE2 Coach** bridges this gap. By entering a snapshot of their game state (civ matchup, ELO, stockpile, villager count, sighted enemy units/buildings), the system uses a **hybrid ML + Expert Rules + LLM Explanation Engine** to deliver prioritized, skill-adapted recommendations (e.g., army composition, economic gatherer redistribution, tactical stance, and critical timing milestones).

```
   +-------------------------------------------------------------------------------+
   |                             USER INTERACTION (WEB UI)                         |
   |   - Quick 30-sec Match Setup (Civs, ELO, Map, Age)                            |
   |   - Mid-Game Snapshot (Villagers, Stockpile, Sighted Enemy Units/Techs)       |
   +---------------------------------------+---------------------------------------+
                                           |
                                           v
   +-------------------------------------------------------------------------------+
   |                             FASTAPI BACKEND GATEWAY                           |
   +---------------------------------------+---------------------------------------+
                                           |
                   +-----------------------+-----------------------+
                   |                                               |
                   v                                               v
   +-------------------------------+               +-------------------------------+
   |     ML STRATEGY INFERENCE     |               |      AOE2 KNOWLEDGE & RULES   |
   |  - Win-Rate & Value Estimator |               |  - Strict Tech Trees & Civs   |
   |  - High-ELO Action Predictor  |               |  - Damage/Armor Counter Matrix|
   |  - Optimal Resource Balancer  |               |  - Macro Production Formulas  |
   +---------------+---------------+               +---------------+---------------+
                   |                                               |
                   +-----------------------+-----------------------+
                                           |
                                           v
   +-------------------------------------------------------------------------------+
   |                      LLM TACTICAL EXPLANATION LAYER                           |
   |   - Translates numeric predictions into clear, prioritized advice             |
   |   - Calibrates complexity to player ELO (Micro tips vs Macro fundamentals)    |
   +---------------------------------------+---------------------------------------+
                                           |
                                           v
   +-------------------------------------------------------------------------------+
   |                       ACTIONABLE TACTICAL DASHBOARD                           |
   |  1. Immediate Military Response (Counters & Buildings)                        |
   |  2. Economic Rebalancing (Villager Target Breakdown)                          |
   |  3. Strategic Stance & Timing Window (Aggressive vs Defensive)                |
   +-------------------------------------------------------------------------------+
```

---

## 1. System Architecture & Components

The platform is architected into five modular subsystems:

1. **Replay Ingestion & Training Pipeline (Offline)**: Scrapes thousands of public recorded games (`.aoe2record`) from `aoe2recs.com` and AoE2 match databases, parses binary operation streams, reconstructs time-series game states with simulated fog-of-war, and builds a feature dataset.
2. **Machine Learning Core (Inference Engine)**:
   - **Strategic Classifier & Action Recommender (Imitation Learning / XGBoost / Deep Neural Net)**: Predicts the highest-win-rate actions (unit production, tech research, building placement) given the partial state.
   - **Economic Optimizer (Constrained Regression / Linear Programming)**: Computes optimal villager distribution (Food, Wood, Gold, Stone) to sustain recommended production without floating idle resources.
3. **AoE2 Domain Knowledge & Counter-Matrix Engine (Deterministic)**: Hard-coded game rules, civilization bonuses, unique technologies, armor classes (cavalry, archer, pierce, bonus damage), and upgrade dependencies.
4. **Natural Language Coaching & Explanation Engine (LLM)**: Transforms raw ML output and rule evaluations into friendly, high-impact natural language coaching, tailored to the player's ELO bracket.
5. **Real-Time Web Application (Frontend + Fast API Gateway)**: Ultra-low-friction, mobile/desktop-friendly interface built for rapid entry during active gameplay (under 20–30 seconds), with visual icon pickers and preset buttons.

---

## 2. Replay Data Pipeline & Dataset Generation

### 2.1 Replay Collection & Ingestion Strategy
- **Source**: Public recorded games from `https://aoe2recs.com/`, `aoe2insights.com`, and community replay dumps.
- **Dataset Size Target**: 50,000+ ranked 1v1 and Team Game replays across diverse ELO tiers (800–1200 ELO beginner/intermediate, 1200–1600 advanced, 1600–2400+ top competitive).
- **Automated Harvester**:
  - Headless crawler / API fetcher downloading matches with metadata (patch version, map, ladder rating, winner).
  - Patch Filtering: Restrict training data to Definitive Edition patches (e.g., Version 101.102.x+) to avoid obsolete balance statistics.

### 2.2 Binary Replay Parsing
Using modern Rust-backed Python bindings (`aoe2rec-py` / `aoe2rec` and `aoc-mgz`):
- **Header Parsing**: Game settings, map size/type, player civ IDs, starting positions, initial resources, ratings.
- **Action/Operation Stream Parsing**: Process operations (`Sync`, `Command`, `Build`, `Train`, `Research`, `Move`, `Attack`, `Tribute`, `Resign`) across game duration timestamps.

```
.aoe2record Binary File
   │
   ├──> Header Extraction ──────> [Civs, Map Type, ELOs, Modifiers]
   │
   └──> Operation Stream ───────> Reconstruct Game State at t = [5, 10, 15, 20, 25, 30...] min
                                   ├── Player Snapshot (Economy, Techs, Army, Buildings)
                                   ├── Opponent Sighted Snapshot (Visible Units, Buildings)
                                   └── Winning Outcome Label (Winner vs Loser actions)
```

### 2.3 Partial Observability & Fog-of-War Simulation
A crucial challenge in RTS data is that **a live player only knows what they have scouted**. Training a model on the ground-truth hidden enemy state would make it useless for a player who doesn't possess complete map vision.

To solve this, our replay processor simulates **Player Perspective Fog-of-War**:
1. **Field of View (FoV) Tracking**: At every interval $t$, compute the player's vision radius around units, buildings, and scout paths.
2. **Sighted Entity Memory**: Record only the enemy units, buildings, and tech upgrades that entered the player's line of sight up to time $t$.
3. **Observation Decay**: Maintain a "last seen" timestamp and count for enemy units (e.g., "5 Berserkers seen 90 seconds ago near East woodline").

### 2.4 State-Action-Outcome Snapshot Extraction
For every game, snapshots are generated at 2-minute increments from $t = 6:00$ to $t = 45:00$:

| Feature Group | Features Extracted |
| :--- | :--- |
| **Match Context** | Map ID (Arabia, Arena, Nomad, etc.), Game Mode (1v1, 2v2, 4v4), Match Length, Player ELO, Opponent ELO |
| **Player Civ & Opponent Civ** | Categorical Civ IDs (45+ civs) with one-hot / entity embeddings |
| **Current Game Time** | Game time in seconds ($t$), Current Age (Dark, Feudal, Castle, Imperial) |
| **Player Economy** | Food, Wood, Gold, Stone stockpiles, Villager total, Villagers per resource, Idle villager time, Active Trade carts, Relics held |
| **Player Military & Tech** | Count of Archers, Knights, Pikes, Skirms, Siege, Monks, Unique Units, Blacksmith upgrades (Melee/Pierce Armor, Attack), Eco upgrades |
| **Observed Opponent State** | Sighted enemy military unit counts, Sighted production buildings (e.g., 2 Ranges, 1 Stable, Castle), Estimated opponent Age |
| **Target Labels (Next 3–5 min)** | Winning player's subsequent actions: Unit production focus, Tech choices, Building constructions, Win/Loss flag ($y \in \{0, 1\}$) |

---

## 3. Machine Learning & Decision Engine

The recommendation system uses a **tri-tier hybrid architecture**:

```
                       ┌──────────────────────────────┐
                       │      User Match Input        │
                       └──────────────┬───────────────┘
                                      │
                                      ▼
             ┌──────────────────────────────────────────────────┐
             │       Feature Vectorizer & State Encoder         │
             └──────────┬────────────────────────────┬──────────┘
                        │                            │
                        ▼                            ▼
     ┌────────────────────────────────────┐   ┌──────────────────────────────────┐
     │      Machine Learning Core         │   │   Deterministic Rules Engine     │
     │ 1. Value Model: P(Win | State)     │   │ 1. Civ Tech Tree Constraints     │
     │ 2. Action Model: Top-ELO Strategy  │   │ 2. Dynamic Damage/Armor Matrix   │
     │ 3. Eco Model: Villager Allocation  │   │ 3. Hard Counter Thresholds       │
     └──────────────────┬─────────────────┘   └──────────────────┬───────────────┘
                        │                                        │
                        └──────────────────┬─────────────────────┘
                                           │
                                           ▼
                       ┌────────────────────────────────────────┐
                       │     Candidate Strategy Selector        │
                       │     (Filter illegal/low-value moves)   │
                       └──────────────────┬─────────────────────┘
                                          │
                                          ▼
                       ┌────────────────────────────────────────┐
                       │      LLM Tactical Explainer            │
                       │  (Generates natural, coaching advice)  │
                       └────────────────────────────────────────┘
```

### 3.1 Model 1: Strategic Action & Counter-Composition Model
- **Model Family**: LightGBM / Multi-head Deep Neural Network with Civilization Embeddings.
- **Objective**: Given current match state and sighted enemy forces, predict the distribution of units and buildings that yield the highest win rate among high-ELO players ($>1600$ ELO).
- **Loss Function**: Weighted Cross-Entropy conditioned on match outcome:
$$\mathcal{L} = - \sum_{i} w_{\text{winner}} \cdot y_i \log(\hat{y}_i)$$
- **Output**: Ranked action candidates:
  - Primary military unit to produce (e.g., *Cavalry / Knight Line*: 78% confidence).
  - Secondary support unit (e.g., *Scorpion / Monk*).
  - Key structural response (e.g., *Drop 2 additional Stables, 1 Monastery*).
  - Key Blacksmith / University tech priorities (e.g., *Scale Barding Armor $\rightarrow$ Bloodlines $\rightarrow$ Husbandry*).

### 3.2 Model 2: Economic Rebalancer & Gatherer Optimization
- **Problem**: New players chronically suffer from imbalanced economies (e.g., 1,500 excess wood and 40 food while wanting to make Knights).
- **Solution**: Economic solver combining empirical high-ELO ratios with linear production rates:
  - Base Villager Gathering Rates:
    - Food (Farms): $\approx 0.35$ food/sec (with Wheelbarrow: $0.38$)
    - Wood: $\approx 0.39$ wood/sec (with Double-Bit Axe: $0.44$)
    - Gold (Mining): $\approx 0.38$ gold/sec
    - Stone (Mining): $\approx 0.36$ stone/sec
  - Production Cost Solver: To produce continuous Knights from 3 Stables ($60\text{F}, 75\text{G}$ every 30s) + continuous Villager production from 2 TCs ($50\text{F}$ every 25s), the model outputs the precise gatherer target:
    - $\text{Food Villagers} = 18$, $\text{Gold Villagers} = 14$, $\text{Wood Villagers} = 8$, $\text{Stone Villagers} = 0$.
    - Current vs. Target Delta: "Move 6 villagers from Wood to Gold and reseed 4 Farms."

### 3.3 Model 3: Stance & Timing Predictor
- **Classifies Game Posture**: `All-in Aggression`, `Forward Pressure`, `Defensive Turtling`, `Fast Imperial Boom`, or `Relic / Hill Control`.
- **Timing Window Alert**: Evaluates power spikes (e.g., enemy Vikings in early Castle Age vs. Imperial Age Berserker upgrade; enemy reaching Castle Age with Camels vs. your Knights).

### 3.4 Deterministic Rules & Tech Tree Guardrails
To prevent ML hallucinations or recommending invalid game actions:
1. **Hard Tech Tree Constraints**: 
   - Aztecs/Mayans/Incas cannot build Stables or make Cavalry.
   - Britons cannot build Stable Paladins.
   - Meso civs get Eagle Warriors; Gurjaras get Shrivamsha Riders.
2. **Hard Counter Table**:
   - High Berserker count $\rightarrow$ Heavy Melee Infantry $\rightarrow$ Countered by Hand Cannoneers, Heavy Cav (Knights/Paladin), Archery Line (Crossbow/Arbalest with kiting), or Cataphracts / Jag Warriors.
   - Heavy Cavalry $\rightarrow$ Countered by Spearmen/Pikemen/Halberdiers, Monks, Camels.
   - Heavy Archer/Crossbow balls $\rightarrow$ Countered by Skirmishers, Mangonels/Onagers, Knights.

---

## 4. LLM Tactical Explainer & Natural Language Generation

While raw ML predictions provide numbers (e.g., `make_cavalry: 0.82`, `target_farms: 18`), new players need **reasoning, context, and clear instructions**.

### 4.1 Prompt Engineering & Dynamic Context Assembly
The backend compiles the game state, ML probabilities, and rule results into a compact structured prompt sent to an ultra-fast LLM (e.g., Gemini 2.5 Flash / Flash Lite):

```json
{
  "player_civ": "Franks",
  "opponent_civ": "Vikings",
  "player_elo": 950,
  "game_time": "22:30 (Castle Age)",
  "resources": {"food": 320, "wood": 750, "gold": 120, "stone": 450},
  "villagers": {"total": 48, "food": 14, "wood": 26, "gold": 6, "stone": 2},
  "sighted_enemy": [{"unit": "Berserk", "count": 5}, {"building": "Castle", "count": 1}],
  "ml_recommendation": {
    "unit_focus": "Knight Line",
    "building_target": "3 Stables total (build 2 more)",
    "eco_adjustment": "Shift 8 wood villagers to farms (food) and 4 to gold",
    "tactical_stance": "Aggressive Castle Age timing before Viking Imp Berserkergang"
  }
}
```

### 4.2 ELO-Calibrated Coaching Tone
- **Beginner Tier (<1000 ELO)**: Focus on simple macro, basic counters, spending excess stockpiles, and avoiding common traps (e.g., "Don't float wood, build production buildings, don't get housed").
- **Intermediate Tier (1000–1400 ELO)**: Adds strategic timing windows, upgrade priority, map control, and relic collection.
- **Advanced Tier (>1400 ELO)**: Focuses on micro engagements, hill advantage, composition transitions, and military power spikes.

---

## 5. Web Application & Real-Time User Experience

Because AoE2 matches are played at standard $1.7\times$ speed, entering data cannot take more than 20–30 seconds.

### 5.1 Rapid Input Wizard (Under 30 Seconds)

```
========================================================================
                      AoE2 REAL-TIME COACH
========================================================================
[Step 1: Match Setup] (Can be saved prior to match start)
  - Your Civ: [ Franks ▾ ]        Enemy Civ: [ Vikings ▾ ]
  - Map: [ Arabia ▾ ]             Your ELO: [ 950 ]
------------------------------------------------------------------------
[Step 2: Live Snapshot] (Quick Sliders & Taps)
  - Game Age:  ( ) Dark   ( ) Feudal   (●) Castle   ( ) Imperial
  - Villagers: [ - | 48 | + ]     Stockpile: [ F: 320 | W: 750 | G: 120 | S: 450 ]
  - Military:  [ 4 Scouts, 2 Knights ]

[Step 3: What Have You Seen?] (Visual Icon Picker with + / -)
  [ ⚔️ Berserker (x5) ]  [ 🏰 Castle (x1) ]  [ 🏹 Archers (x0) ]
  [ + Add Sighted Unit / Building ]

------------------------------------------------------------------------
                 [ ⚡ GET TACTICAL RECOMMENDATION ⚡ ]
========================================================================
```

### 5.2 Tactical Output Dashboard

The result is displayed as high-visibility tactical cards:

```
+----------------------------------------------------------------------+
| 🎯 PRIMARY DIRECTIVE: CASTLE AGE CAVALRY PUSH                        |
| "Enemy is investing in Berserkers without anti-cavalry defense.     |
| Exploit your Franks heavy cavalry advantage now!"                   |
+----------------------------------------------------------------------+

| ⚔️ Military Action Plan:
|  - Produce: Knights from 3 Stables (Build 2 additional Stables now).
|  - Blacksmith: Prioritize Scale Barding Armor & Bloodlines.
|  - Counter Note: Sighted 5 Berserkers — Knights easily overpower
|    Castle Age infantry.

| 🌾 Economic Balancing:
|  - Problem: You are floating 750 Wood while starving on Food & Gold.
|  - Action: Immediately send 8 Woodchoppers to build Farms.
|  - Target Allocation: 22 Food | 14 Wood | 10 Gold | 2 Stone

| ⏳ Strategic Timing Window:
|  - ATTACK WINDOW: Next 3–5 minutes.
|  - Danger: Do not let Vikings mass Elite Berserker + Berserkergang in
|    Imperial Age. Strike before they reach Imp!
+----------------------------------------------------------------------+
```

---

## 6. Technical Stack & Architecture

```
+---------------------------------------------------------------------+
| FRONTEND LAYER                                                      |
| - Framework: Next.js 15 (React 19) + TypeScript                     |
| - Styling: Tailwind CSS + Shadcn UI (High-contrast RTS Dark Mode)   |
| - State Management: Zustand (persists civs, quick reload)           |
| - Asset Library: AoE2DE high-res civ/unit/tech icons & sprites      |
+---------------------------------------------------------------------+
                                 │ HTTP / JSON API
                                 ▼
+---------------------------------------------------------------------+
| BACKEND API GATEWAY                                                 |
| - Framework: FastAPI (Python 3.12+ / 3.13)                          |
| - Task Queue / Cache: Redis + Celery / AsyncIO                      |
| - Validation: Pydantic v2 schemas                                   |
+---------------------------------------------------------------------+
           │                                 │
           ▼                                 ▼
+-----------------------+         +-----------------------------------+
| ML INFERENCE SERVICE  |         | AOE2 KNOWLEDGE & RULES ENGINE     |
| - Engine: ONNX Runtime|         | - Tech Tree JSON Graph            |
| - Model: LightGBM /   |         | - Armor / Damage Class Resolver   |
|   PyTorch MLP         |         | - Economy Rate Equations          |
+-----------------------+         +-----------------------------------+
           │                                 │
           └────────────────┬────────────────┘
                            ▼
+---------------------------------------------------------------------+
| LLM TACTICAL EXPLANATION SERVICE                                    |
| - Model: Gemini 2.5 Flash / Flash Lite (via Vertex AI / Google AI)   |
| - Latency: <300ms streaming responses                               |
+---------------------------------------------------------------------+
```

---

## 7. Data Schema & Ingestion Specifications

### 7.1 Parsed Match Snapshot Schema
```json
{
  "match_id": "502556700",
  "patch_version": "101.102.x",
  "timestamp_sec": 1200,
  "map_type": "Arabia",
  "player": {
    "civ_id": 35,
    "civ_name": "Franks",
    "elo": 950,
    "age": 3,
    "resources": {"food": 320, "wood": 750, "gold": 120, "stone": 450},
    "villagers": {"total": 48, "food": 14, "wood": 26, "gold": 6, "stone": 2},
    "military_units": {"knight": 2, "scout_cavalry": 4},
    "buildings": {"town_center": 2, "barracks": 1, "stable": 1, "blacksmith": 1},
    "completed_techs": ["wheelbarrow", "double_bit_axe", "horse_collar"]
  },
  "opponent_observed": {
    "civ_id": 22,
    "civ_name": "Vikings",
    "estimated_age": 3,
    "sighted_units": [{"unit": "berserk", "count": 5, "last_seen_sec": 1140}],
    "sighted_buildings": [{"building": "castle", "count": 1}]
  },
  "label": {
    "winner": true,
    "next_unit_produced": "knight",
    "next_tech_researched": "scale_barding_armor",
    "next_building_built": "stable"
  }
}
```

---

## 8. Step-by-Step Implementation Roadmap

```
                               PROJECT ROADMAP
══════════════════════════════════════════════════════════════════════════════
Phase 1: Replay Pipeline & Dataset Mining        [Weeks 1-3]
Phase 2: Rules Engine & Counter Matrix           [Weeks 3-4]
Phase 3: Machine Learning Model Development      [Weeks 5-7]
Phase 4: LLM Explanation Engine & Prompting      [Weeks 7-8]
Phase 5: Web UI / UX Fast Entry Application     [Weeks 9-11]
Phase 6: Integration, ELO Calibration & Launch   [Weeks 12-13]
══════════════════════════════════════════════════════════════════════════════
```

### Phase 1: Replay Pipeline & Ingestion (`Weeks 1–3`)
- [x] Integrate Rust parser (`aoe2rec-py` / `aoe2rec`) for fast batch parsing of `.aoe2record` files.
- [x] Build automated scraper to pull ranked match replays and metadata from match APIs and `aoe2recs.com`.
- [x] Implement Fog-of-War line-of-sight simulator to extract player-visible states.
- [x] Export game snapshot vectors across time slices into Parquet format.

### Phase 2: Domain Rules & Counter-Matrix Engine (`Weeks 3–4`)
- [x] Encode complete AoE2:DE unit and tech tree graphs (all 45+ civs, bonuses, unique units).
- [x] Implement the AoE2 Armor Class & Damage Formula engine (Pierce, Melee, Bonus vs Cavalry, Archer, Infantry, Siege).
- [x] Build the real-time Villager Production-Balance Calculator (resource consumption vs gather rates).

### Phase 3: Machine Learning Model Development (`Weeks 5–7`)
- [ ] Train Strategy Classifier (predicting winning unit compositions & buildings from partial states).
- [ ] Train Win Probability Estimator ($P(\text{Win} \mid s, a)$).
- [ ] Train Economic Rebalancer model against high-ELO macro distributions.
- [ ] Convert models to ONNX format for sub-20ms inference latency.

### Phase 4: LLM Explanation Engine (`Weeks 7–8`)
- [ ] Develop structured JSON prompting pipeline for Gemini 2.5 Flash.
- [ ] Implement ELO-tiered explanation filters (Beginner vs Intermediate vs Advanced advice).
- [ ] Build hallucination verification: Ensure LLM explanations strictly match tech tree rules and ML candidate outputs.

### Phase 5: Web Application Frontend & UX (`Weeks 9–11`)
- [ ] Build Next.js 15 application with high-contrast RTS dark mode styling.
- [ ] Implement 30-Second Match & Mid-game Wizard with unit/building visual icons.
- [ ] Implement real-time voice-to-text / speech input option (e.g. player speaks: *"I see 5 Berserkers and I have 700 wood"*).
- [ ] Build interactive Tactical Dashboard with actionable checklists and gatherer sliders.

### Phase 6: Testing, Calibration & Deployment (`Weeks 12–13`)
- [ ] Benchmark recommendations against top-tier streamer / pro-player tournament matches.
- [ ] Conduct user testing with 800–1200 ELO beginner players during live matches.
- [ ] Deploy backend on containerized Kubernetes/Cloud Run and frontend on Vercel/Cloudflare CDN.

---

## 9. Risk Analysis & Mitigation Strategies

| Risk | Impact | Mitigation Strategy |
| :--- | :--- | :--- |
| **Data Drift (New AoE2 Patches/DLCs)** | Medium | Maintain modular patch version tagging; re-run parsing pipeline when major balance patches drop; decouple rules engine from ML weights. |
| **In-Game Time Friction** | High | Design UI for $\le 30$s interaction; use one-click counters; provide voice input; keep match setup pre-loaded before the game starts. |
| **Partial scouting hallucinations** | High | Condition model strictly on *observed* enemy units; provide probabilistic scouting tips (e.g., *"No barracks seen yet, scout around minute 10 for hidden archery ranges"*). |
| **Low-ELO Execution Overload** | Medium | Calibrate advice based on user ELO; prioritize 1-2 major macro fixes rather than giving 10 complex micro commands. |

---

## 10. Future Horizons (Post-MVP)

1. **Desktop Companion Overlay (Overwolf / Local Hook)**: Direct memory or savegame auto-reader that reads the game state automatically in real-time without manual user input.
2. **Audio Coach (Voice Assistant)**: A spoken AI co-pilot that whispers timing alerts and reminders through player headphones (e.g., *"Remember to reseed farms in 30 seconds"*).
3. **Post-Game Replay Reviewer**: Upload your `.aoe2record` after a match to get an automated timestamped coaching review highlighting your mistakes and turning points.
