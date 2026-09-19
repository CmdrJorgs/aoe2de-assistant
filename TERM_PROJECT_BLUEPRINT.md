# Age of Empires II: Tactical AI Coach — DSC 670 Term Project Blueprint

> **Course**: DSC 670 — Generative AI  
> **Target Project**: *Age of Empires II: Definitive Edition — Real-Time Tactical & Strategic AI Coach (`aoe2-coach`)*  
> **Date**: September 2026  

---

## 1. Executive Summary & Academic Alignment

The `aoe2-coach` system is an advanced decision-support architecture designed to assist players in *Age of Empires II: Definitive Edition* (AoE2:DE). Real-Time Strategy (RTS) gaming is an ideal domain for Generative AI research because it combines:
- **Complex tabular and state telemetry**: Stockpiles (Food, Wood, Gold, Stone), villager allocations, unit counts, game age, elapsed game time.
- **Deep domain rules**: 45+ unique civilizations, asymmetric tech trees, armor classes, damage multipliers, and counter-matrices.
- **Extreme cognitive constraints under fog-of-war**: Players make split-second decisions with incomplete information.

### Alignment with DSC 670 Rubric

| Course Requirement | `aoe2-coach` Project Adaptation |
| :--- | :--- |
| **Milestone 1 (Week 2)**: Idea, Goals, Approach (APA Paper) | Proposal framing RTS cognitive overload and proposing an ELO-calibrated GenAI coach. |
| **Milestone 2 (Week 4)**: Refined Design & 5 Prompt Experiments | 5 benchmark prompt experiments highlighting failure modes of baseline foundation models (hallucinations, cognitive overload, schema violations). |
| **Milestone 3 (Week 8)**: Fine-Tune OpenAI Model (Jupyter Notebook) | Hosted OpenAI fine-tuning (`gpt-4o-mini`), training tracking via OpenAI API endpoints, loss curve analysis, zero-hallucination verification. *(No LoRA; Jupyter Notebook submission only).* |
| **Milestone 4 (Week 11)**: Final Application (Streamlit & Presentation) | Streamlit dashboard (`streamlit_app.py`) connecting to the fine-tuned model, accompanied by slide presentation and screenshots. |

---

## 2. Core GenAI Thesis: Why Fine-Tuning is Genuinely Useful

In standard prompt engineering, general-purpose LLMs (`gpt-4o-mini`, `gpt-3.5-turbo`, `llama-3.2`) fail in competitive RTS coaching due to four domain-specific challenges:

### 1. Civilization Tech-Tree Hallucinations
General foundation models have loose, associative memory of game lore rather than rigid logical constraints:
- Recommending **Stables, Knights, or Bloodlines** to Mesoamerican civilizations (*Aztecs, Mayans, Incas*).
- Recommending **Paladins** to civilizations without them (e.g., *Britons*).
- Recommending **Imperial Age technologies** to players in Feudal or Castle Age.

### 2. Cognitive Overload & ELO Persona Calibration
Generic models default to verbose, conversational explanations containing 10–15 unranked instructions:
- **Beginner (<1000 ELO)**: When floating 1,500 wood with an idle Town Center, the player cannot execute complex micro. They need **blunt, macro-first triage** limited to $\le 3$ high-impact action items (*"Stop cutting wood. Build 2 Town Centers and seed farms immediately"*).
- **Intermediate (1000–1400 ELO)**: Needs advice focused on civ power spikes, blacksmith upgrade priority (armor vs. attack), and timely military transitions.
- **Advanced (>1400 ELO)**: Requires technical RTS analysis—micro kiting, hill positioning advantage, and precise attack timing windows down to the minute.

### 3. Inference Latency & Token Bloat
Passing complete tech trees, counter formulas, and few-shot examples inside system prompts consumes 2,000–3,500 tokens per request. In an RTS match, coaching advice must arrive in $\le 1\text{s}$. Fine-tuning encodes the domain knowledge into the model weights, minimizing prompt size, latency, and token cost.

### 4. Strict Deterministic JSON Schema Compliance
Real-time web dashboards and HUDs require 100% predictable JSON output without conversational preambles or malformed markdown fences to prevent runtime UI crashes.

---

## 3. Dataset Generation Pipeline (Leveraging Existing Code)

Rather than hand-writing examples, the existing `aoe2-coach` repository contains deterministic engines that act as a **ground-truth synthesizer**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                       TRAINING DATA SYNTHESIS FLOW                          │
├───────────────────────┬─────────────────────────────┬───────────────────────┤
│ Match Telemetry Input │ Deterministic Domain Engine │ Fine-Tuning Target    │
├───────────────────────┼─────────────────────────────┼───────────────────────┤
│ • snapshots.parquet   │ • tech_tree.py              │ OpenAI Chat JSONL     │
│ • pro_datasets.py     │ • counter_matrix.py         │ • Zero hallucinations │
│ • user_testing_calib. │ • economy_solver.py         │ • ELO-calibrated tone │
│ • 45+ Civ Matchups    │ • fallback_engine.py        │ • Strict JSON Schema  │
└───────────────────────┴─────────────────────────────┴───────────────────────┘
```

### Dataset Structure (`train.jsonl` / `val.jsonl`)

Each training row follows the OpenAI Chat fine-tuning schema:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are the Grandmaster AI Tactical Coach for Age of Empires II: Definitive Edition. Provide concise, ELO-calibrated, hallucination-free tactical advice strictly obeying civilization tech trees in JSON format."
    },
    {
      "role": "user",
      "content": "Match State:\nPlayer: Aztecs | ELO: 920 (Beginner) | Age: Castle Age (21:30)\nResources: Food: 150, Wood: 1200, Gold: 180, Stone: 100\nVillagers: Food: 8, Wood: 28, Gold: 6, Stone: 0\nSighted Enemy: 14 Frankish Knights, 2 Stables\nPlayer Military: 4 Crossbowmen"
    },
    {
      "role": "assistant",
      "content": "{\"primary_directive\":\"PIKEMAN & MONK DEFENSE\",\"coach_summary\":\"You are floating severe excess wood while Frankish knights are raiding. Aztecs have no cavalry—switch woodcutters to farms and mass Pikemen.\",\"elo_tier\":\"beginner\",\"military_plan\":{\"primary_unit_recommendation\":\"Pikeman\",\"secondary_unit_recommendation\":\"Monk\",\"production_building_instruction\":\"Build 2 additional Barracks (3 total)\",\"key_tech_priorities\":[\"Pikeman\",\"Scale Mail Armor\"],\"counter_explanation\":\"Pikemen deal massive bonus damage against Frank cavalry with zero gold cost.\",\"micro_positioning_tip\":\"Keep Pikemen stationed on top of your woodline and farms; do not chase scouts in open fields.\"},\"economic_plan\":{\"problem_diagnosis\":\"Severe wood float (1200 wood) with food starvation.\",\"immediate_action\":\"Pull 10 lumberjacks immediately to seed farms around your Town Center.\",\"target_villager_allocation\":{\"food\":18,\"wood\":18,\"gold\":8,\"stone\":0},\"macro_tip\":\"Spend your wood as soon as it crosses 200 by building farms or production buildings.\"},\"timing_plan\":{\"posture\":\"Defensive Turtling\",\"attack_window\":\"Next 5 minutes\",\"threat_alert\":\"Frank Castle Age cavalry power spike active\",\"strategic_spike_reasoning\":\"Defend until Pikeman numbers reach 20+, then add Monks to convert forward Knights.\"},\"priority_checklist\":[\"1. Move 10 lumberjacks to build 10 farms\",\"2. Construct 2 Barracks immediately\",\"3. Queue continuous Pikemen production\"]}"
    }
  ]
}
```

---

## 4. Milestone-by-Milestone Execution Roadmap

```
Week 2 ───► Milestone 1: Formal Proposal & Research Strategy (APA Paper)
Week 4 ───► Milestone 2: Problem Refinement & 5 Prompt Experiments (Paper + Code)
Week 8 ───► Milestone 3: Model Fine-Tuning & Metrics Tracking (Jupyter Notebook)
Week 11 ──► Milestone 4: Streamlit Web Application & Final Presentation
```

---

### Milestone 1 (Week 2): Pick Your Project

- **Deliverable**: Formal paper in APA format.
- **Sections**:
  1. **Description of the Idea**:
     - Cognitive overload in RTS gameplay.
     - Limitations of retrospective analytics (AoE2Insight, CaptureAge) vs. real-time decision support.
  2. **Main Goal(s)**:
     - Develop an AI Tactical Coach capable of turning raw match telemetry into real-time, ELO-calibrated natural language directives.
     - Achieve 0% tech-tree hallucinations and 100% JSON schema compliance.
  3. **Initial Approach**:
     - Extract game state vectors from replay logs (`.aoe2record` / `.parquet`).
     - Utilize domain rules engines (counter matrices, LP economy solvers) as knowledge anchors.
     - Fine-tune a foundation model (OpenAI) to deliver natural language tactical plans.

---

### Milestone 2 (Week 4): Refine Your Project & 5 Prompt Experiments

- **Deliverables**: Formal paper (APA format) + Prompt experiment code.
- **Content**:
  1. **Updated Problem Statement**: Detail the specific challenge of multi-modal match state interpretation under time pressure.
  2. **Model Selection**: Foundation model: OpenAI `gpt-4o-mini` (fastest turnaround, high structured output compliance, cost-efficient fine-tuning).
  3. **5 Prompt Experiments**:
     - **Experiment 1 (Tech-Tree Constraint Test)**:
       - *Setup*: Prompt model with Mesoamerican civ (Aztecs) facing heavy cavalry.
       - *Observation*: Baseline zero-shot model suggests "build Stables or train Knights/Camels" (violates tech tree).
       - *Significance*: Establishes the necessity of domain fine-tuning.
     - **Experiment 2 (Cognitive Load & ELO Persona Calibration)**:
       - *Setup*: Low-ELO scenario (850 ELO) with severe resource floating.
       - *Observation*: Base model gives a 15-point multi-paragraph essay.
       - *Significance*: Fine-tuning needed to force strict $\le 3$ action item limit for beginners.
     - **Experiment 3 (Counter-Matrix Tactical Accuracy)**:
       - *Setup*: Opponent masses Crossbowmen + Spearmen.
       - *Observation*: Evaluate whether model recommends Mangonels + Skirmishers vs. incorrect cavalry counters.
     - **Experiment 4 (Strict JSON Output Reliability)**:
       - *Setup*: Stress test with complex match state asking for structured schema.
       - *Observation*: Evaluate schema missing-key rate and extraneous markdown text in base models.
     - **Experiment 5 (Economic Rebalancing Directives)**:
       - *Setup*: Mismatched villager allocation for desired military production (e.g. 20 on gold, 4 on wood).
       - *Observation*: Test whether the model correctly diagnoses macro leaks and prescribes numerical villager shifts.
  4. **Fine-Tuning Strategy (Looking ahead to Week 7/8)**:
     - Describe the supervised fine-tuning dataset generation pipeline, prompt schema, and loss tracking goals.

---

### Milestone 3 (Week 8): Build Your First Model

- **Critical Rubric Requirement**: **Must be built entirely within a Jupyter Notebook (`.ipynb`)** using the OpenAI Fine-Tuning API. *(Do not use LoRA; use OpenAI full hosted fine-tuning).*
- **Notebook Implementation Workflow (`notebooks/Milestone3_FineTuning.ipynb`)**:

```python
# 1. Initialize OpenAI Client
import os
import time
import json
import matplotlib.pyplot as plt
import pandas as pd
from openai import OpenAI

client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# 2. Upload Training & Validation Files
train_file = client.files.create(
    file=open("data/finetune/aoe2_coach_train.jsonl", "rb"),
    purpose="fine-tune"
)
val_file = client.files.create(
    file=open("data/finetune/aoe2_coach_val.jsonl", "rb"),
    purpose="fine-tune"
)

# 3. Launch Fine-Tuning Job
job = client.fine_tuning.jobs.create(
    training_file=train_file.id,
    validation_file=val_file.id,
    model="gpt-4o-mini",
    hyperparameters={"n_epochs": 3}
)

# 4. Track Build Events via Endpoints (as demonstrated in Chapter 7)
while True:
    status = client.fine_tuning.jobs.retrieve(job.id)
    print(f"Status: {status.status}")
    if status.status in ["succeeded", "failed", "cancelled"]:
        break
    time.sleep(30)

# 5. Extract and Plot Training Metrics
events = client.fine_tuning.jobs.list_events(fine_tuning_job_id=job.id, limit=100)
# Extract training_loss, validation_loss, and full token accuracy curves...
```

- **Notebook Evaluation & Commentary**:
  - Run comparative benchmark tests on 15 held-out test scenarios (`aoe2_coach/benchmarks/pro_datasets.py`).
  - Calculate and report:
    - **Tech-Tree Hallucination Rate**: Base Model ($\sim 25\text{--}40\%$) vs. Fine-Tuned Model ($0\%$).
    - **JSON Validation Rate**: Base Model ($\sim 85\%$) vs. Fine-Tuned Model ($100\%$).
    - **ELO Action Limit Compliance**: Base Model ($\sim 40\%$) vs. Fine-Tuned Model ($100\%$).
  - In-depth Markdown commentary reflecting on training loss convergence and domain adaptation.

---

### Milestone 4 (Week 11): Final Application (Streamlit) & Presentation

- **Critical Rubric Requirement**: **Streamlit web application (`.py` files)** with presentation slides (PowerPoint/Sway) and screenshots or video.
- **Streamlit App Architecture (`streamlit_app.py`)**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    STREAMLIT TACTICAL COACH DASHBOARD                       │
├───────────────────────┬─────────────────────────────────────────────────────┤
│ SIDEBAR CONTROLS      │ MAIN COACHING VIEW                                  │
├───────────────────────┼─────────────────────────────────────────────────────┤
│ • Match Setup         │ 1. Tactical Directive Header (Banner)               │
│   - Player / Opp Civ  │    "CASTLE AGE CAVALRY PUSH" (Urgency: High)        │
│   - Age / Game Time   │ 2. ELO-Calibrated Coach Commentary                  │
│   - Player ELO Slider │ 3. Military & Counter Plan                          │
│ • Telemetry Input     │    - Primary Unit + Tech Upgrade Order              │
│   - Stockpile Sliders │    - Micro & Positioning Guidance                   │
│   - Villager Sliders  │ 4. Macro Economy Rebalancer                         │
│ • Sighted Enemy Units │    - Villager Reallocation Table                    │
│ • Model Selector:     │    - Floating Stockpile Warning                     │
│   [Base vs Fine-Tuned]│ 5. Side-by-Side Model Comparator (Base vs FT)       │
└───────────────────────┴─────────────────────────────────────────────────────┘
```

- **Deliverables**:
  1. `streamlit_app.py` and modular backend Python files.
  2. Professional presentation deck (PowerPoint or Sway):
     - Background and RTS Cognitive Problem.
     - Model Architecture & Dataset Distillation.
     - Fine-Tuning Loss Metrics & Verification Results.
     - Application Architecture & Streamlit Live Demo Screenshots.
  3. Optional demo video demonstrating real-time tactical adjustments.

---

## 5. Summary Checklist of Next Actions

- [ ] **Week 2**: Submit Milestone 1 APA paper articulating the problem, goals, and GenAI approach.
- [ ] **Week 4**: Execute the 5 baseline prompt experiments; submit Milestone 2 APA paper and code.
- [ ] **Week 6–7**: Run `scripts/generate_finetune_dataset.py` to produce 200–300 verified JSONL training pairs.
- [ ] **Week 8**: Execute `Milestone3_FineTuning.ipynb` on OpenAI, track metrics via API endpoints, and submit the completed Jupyter Notebook.
- [ ] **Week 11**: Polish `streamlit_app.py`, capture screenshots, build the presentation deck, and finalize the term project.
