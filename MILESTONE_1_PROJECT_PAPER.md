# Real-Time Generative Tactical Coaching in Asymmetric Real-Time Strategy Games: An Elo-Calibrated Decision Support Architecture for *Age of Empires II: Definitive Edition*

<br>

<div align="center">

**Student Author**  
Department of Data Science and Artificial Intelligence, College of Computing  
DSC 670: Generative AI  
Instructor / Faculty Advisory Committee  
September 16, 2026  

</div>

<br>

---

### **Abstract**

Real-time strategy (RTS) games represent one of the most challenging frontiers in artificial intelligence and human-computer interaction, characterized by imperfect information, immense combinatorial action spaces, and high-frequency cognitive demands under fog-of-war. In complex environments such as *Age of Empires II: Definitive Edition* (AoE2:DE)—which features 45 distinct civilizations, asymmetric technology trees, and multi-resource macroeconomic balancing—human players frequently suffer from severe cognitive overload. While existing analytical tools provide retrospective, post-mortem statistics (e.g., CaptureAge, AoE2Insights), players lack in-situ, real-time decision support capable of translating live telemetry into actionable tactical directives. General-purpose foundation large language models (LLMs) deployed zero-shot fail catastrophically in this domain due to civilization tech-tree hallucinations, excessive verbosity, high inference latency, and schema unreliability. This paper proposes `aoe2-coach`, a generative decision-support architecture that synthesizes live match telemetry into concise, skill-adapted tactical recommendations. Leveraging a hybrid neuro-symbolic framework that couples deterministic domain engines (strict technology trees, combat counter matrices, and continuous rate-drain economic optimization solvers) with a hosted fine-tuned transformer model (Google `gemini-1.5-flash` on Google Cloud), the system produces skill-calibrated coaching directives tailored to player rating (Elo) tiers. By executing on Google's serverless cloud infrastructure, the architecture incurs $0 standby hosting costs and introduces zero local GPU, VRAM, or CPU resource contention on the host machine running the game. This milestone proposal formalizes the project concept, delineates four core operational and empirical goals, outlines the initial end-to-end methodological approach, and discusses anticipated design evolutions across the project lifecycle.

*Keywords:* Generative AI, Real-Time Strategy, Cognitive Load Theory, Supervised Fine-Tuning, Elo Calibration, Tech-Tree Grounding, Decision Support Systems, Age of Empires II, Transformer Models

---

<br>

## **Introduction and Contextual Foundation**

In competitive decision-making environments characterized by rapid information flow, partial observability, and strict temporal deadlines, human decision-makers encounter profound cognitive friction. Real-time strategy (RTS) video games represent an ideal empirical paradigm for investigating these cognitive and computational dynamics (Buro, 2003; Ontañón et al., 2013). Unlike turn-based games such as chess or Go, in which players possess perfect information and discrete planning intervals (Silver et al., 2018), RTS environments force participants to continuously execute physical and mental operations across concurrent strategic dimensions under imperfect map vision (Vinyals et al., 2019).

Among modern competitive RTS games, *Age of Empires II: Definitive Edition* (AoE2:DE) presents an exceptionally complex domain. Featuring 45 historically differentiated civilizations, deeply asymmetric technology trees, multi-resource macroeconomic chains (Food, Wood, Gold, Stone), and an intricate damage-multiplier counter matrix, the game demands continuous simultaneous reasoning across macroeconomic optimization ("macro") and micro-tactical army control ("micro"). Players routinely fail not because optimal strategic counter-play is unknown, but because the cognitive throughput required to synthesize raw telemetry, evaluate tech-tree dependencies, and execute counter-maneuvers exceeds human working memory capacity under match pressure (Sweller, 1988).

To bridge this operational divide, this project introduces `aoe2-coach`, an Elo-calibrated, hallucination-free generative tactical coach. This paper establishes the formal project proposal for Milestone 1 of DSC 670 (Generative AI), presenting a detailed description of the project idea, articulating primary academic and operational goals, and specifying the initial methodological approach designed to translate complex game telemetry into real-time natural language directives.

---

## **A Description of the Project Idea**

The primary thesis of this project is that generative artificial intelligence—when constrained by deterministic domain rules and calibrated to human cognitive bandwidth—can serve as an effective real-time decision-support coach in complex, asymmetric RTS environments. 

### **Cognitive Overload in Real-Time Strategy Environments**

Human performance in RTS games is severely constrained by working memory limitations, as formalized by Cognitive Load Theory (Sweller, 1988, 2011) and Baddeley's multi-component model of working memory (Baddeley, 1992, 2000). During a competitive AoE2:DE match, a player experiences three compounding sources of cognitive load:

1. **Intrinsic Cognitive Load**: Arising from the inherent mathematical complexity of the game state, including tracking stockpile depletion rates, four-resource gatherer efficiency, military population headrooms, and multi-tier armor-piercing damage formulas across diverse unit types.
2. **Extraneous Cognitive Load**: Induced by the physical mechanics of the user interface, spatial camera navigation across the mini-map, manual queuing of villagers, and spatial building placement under high Actions Per Minute (APM) demands.
3. **Germane Cognitive Load**: The mental effort dedicated to schema acquisition, pattern recognition, identifying strategic opponent transitions through partial scouting cues, and formulating counter-strategies.

Under competitive stress, human players experience "cognitive tunneling" or attentional narrowing (Staal, 2004). Beginner and intermediate players (typically rated between 600 and 1300 Elo on the global ranked ladder) frequently suffer from catastrophic macroeconomic collapse: stockpiling thousands of unused lumber resources ("wood float") while starving for food, permitting Town Centers to sit idle, or failing to scout forward military infrastructure. When an unexpected army transition appears out of the fog-of-war, the player must simultaneously diagnose their economic dysfunction, look up relevant unit counter interactions, verify their civilization's technology tree availability, and execute military re-tasking within a 15-to-30 second window. In the vast majority of cases, cognitive overload induces paralysis or erratic tactical decisions that precipitate match loss.

### **The Retrospective Analytics Gap**

The competitive AoE2:DE ecosystem features sophisticated analytical telemetry tools, most notably CaptureAge (https://captureage.com) and AoE2Insights (https://www.aoe2insights.com). CaptureAge provides live broadcast overlays displaying real-time floating resources, worker allocations, idle Town Center percentages, and army values, while AoE2Insights parses recorded binary replay files (`.aoe2record`) into post-match economic graphs, production timelines, and spatial heatmaps.

Despite their analytical sophistication, these tools suffer from a fundamental structural limitation: they are strictly **retrospective and observational**. They inform players *what happened* or *that an inefficiency occurred*, but they provide zero prescriptive, in-situ guidance explaining *what to do next*. Reviewing a post-match graph that indicates a player floated 1,400 excess wood at minute 22 does not remediate the real-time cognitive failure that caused the mistake during gameplay. Furthermore, raw graphical overlays demand additional visual parsing, exacerbating extraneous cognitive load rather than alleviating it. What players require is an intelligent, low-latency conversational intermediary that ingests the raw telemetry vector and synthesizes it into direct, prioritized, natural language tactical advice.

### **Limitations of General-Purpose Foundation Models**

The emergence of modern transformer-based Large Language Models (LLMs) such as Gemini 1.5 Flash, GPT-4, and Llama 3 offers a promising foundation for automated conversational coaching (Achiam et al., 2023; Brown et al., 2020; Gemini Team, 2024; Ouyang et al., 2022). However, zero-shot and few-shot deployments of general-purpose foundation models consistently fail when applied to real-time competitive RTS coaching due to four domain-specific failure modes:

#### *Civilization Tech-Tree Hallucinations*
Foundation models possess probabilistic, associative recall of historical and gaming literature rather than strict ontological constraints. In AoE2:DE, civilization technology trees are strictly bounded across all 45 civilizations: Mesoamerican civilizations (Aztecs, Mayans, Incas) possess no Stables and cannot produce cavalry; civilizations such as Britons lack the Paladin upgrade; civilizations such as Byzantines lack Bloodlines; and Gothic units benefit from unique infantry cost discounts. In empirical zero-shot baseline queries, off-the-shelf LLMs routinely hallucinate non-existent military options—for example, instructing an Aztec player facing heavy cavalry to "construct two Stables and mass Knights." In a competitive match, executing an impossible directive guarantees defeat.

#### *Cognitive Incongruence and Lack of Elo Persona Calibration*
Generic foundation models default to verbose, academic, multi-paragraph expositions containing 10 to 15 unranked recommendations. While an exhaustive treatise on transition theory might be appreciated in post-match study, delivering a 500-word response to a 900-Elo player during an active cavalry raid overwhelms their remaining working memory. Drawing upon the concept of the Zone of Proximal Development (ZPD; Vygotsky, 1978), effective coaching must calibrate information density to the user's operational competence:
- **Beginner (<1000 Elo)**: Requires strict macroeconomic triage limited to no more than three high-impact, declarative action items (e.g., *"Stop gathering wood; immediately build 2 Town Centers and seed 10 farms"*).
- **Intermediate (1000–1400 Elo)**: Requires guidance focused on civilization power spikes, Blacksmith upgrade sequencing (armor vs. attack priority), and timely military counter-transitions.
- **Advanced (>1400 Elo)**: Requires technical micro-tactical execution tips, hill elevation advantages, kiting strategies, and minute-precise attack timing windows.

#### *High Inference Latency and Context Token Bloat*
Attempting to prevent hallucinations in zero-shot models via exhaustive in-context prompt engineering requires appending massive reference dictionaries—including 45 civilization tech trees, armor class tables, damage calculation formulas, and few-shot exemplars—into the system prompt. This inflates context window consumption by 2,500 to 4,000 tokens per call. The resultant latency (often exceeding 4 to 8 seconds) renders the advice obsolete within the rapid cadence of an RTS match, while drastically escalating API inference costs.

#### *Deterministic Schema Non-Compliance*
To integrate seamlessly into a real-time web dashboard or heads-up display (HUD), the coaching output must strictly adhere to a deterministic JSON schema containing discrete fields for tactical summaries, military counter plans, economic villager redistributions, and action checklists. Base foundation models frequently output conversational preambles (e.g., *"Sure, here is your tactical plan:"*), wrap text in unrequested markdown code fences, omit mandatory JSON keys, or generate syntactically invalid payloads that crash client-side graphical interfaces.

### **The `aoe2-coach` Solution**

The `aoe2-coach` architecture directly addresses these limitations through a hybrid neuro-symbolic approach. By pairing deterministic computational rules engines with hosted supervised fine-tuning of an efficient, transformer-based foundation model (Google `gemini-1.5-flash` hosted via Google AI Studio and Vertex AI), the system distills strict domain logic—tech-tree graph traversals, combat damage matrices, and continuous rate-drain economic formulas—into model weights. Crucially, hosted serverless execution eliminates local hardware competition with *Age of Empires II: Definitive Edition* on the host PC, reserving 100% of local GPU VRAM and CPU cycles for the game simulation while avoiding idle endpoint hosting fees. This delivers instantaneous, zero-hallucination, Elo-calibrated tactical synthesis using compact system prompts.

---

## **The Main Goals of the Project**

To establish a clear scientific trajectory and provide rigorous evaluation criteria, this project defines four primary operational, technical, and pedagogical goals.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          CORE PROJECT OBJECTIVES                            │
├───────────────────────┬─────────────────────────────┬───────────────────────┤
│ Goal Dimension        │ Target Metric / Standard    │ Methodological Focus  │
├───────────────────────┼─────────────────────────────┼───────────────────────┤
│ 1. Tactical Synthesis │ Real-time state translation │ Telemetry digestion   │
│ 2. Elo Calibration    │ 100% adherence to ZPD rules │ Skill-adapted triage  │
│ 3. Domain Integrity   │ 0% tech-tree hallucinations │ SFT + rule grounding  │
│ 4. Output Reliability │ 100% JSON schema validation │ API-grade pipelines   │
└───────────────────────┴─────────────────────────────┴───────────────────────┘
```

### **Goal 1: Real-Time Tactical Synthesis from Multimodal Match Telemetry**

The primary operational goal is to engineer an end-to-end pipeline that converts complex, raw match state vectors into concise, actionable, and human-interpretable natural language directives. The system must successfully digest:
- **Civilization Matchup Parameters**: Player civilization, opponent civilization, current game age (Dark, Feudal, Castle, Imperial), and elapsed game time across all 45 civilizations.
- **Macroeconomic State**: Four-resource stockpiles (Food, Wood, Gold, Stone) and current villager task allocations.
- **Observed Military Intelligence**: Sighted enemy unit counts, forward production buildings, and visible military upgrades filtered through simulated fog-of-war.
- **Player Skill Dimension**: Player ladder rating (Elo) used to dictate pedagogical framing.

The system must output a comprehensive tactical battle plan that addresses military unit production, economic villager reallocation targets, tactical posturing (aggressive forward pressure vs. defensive turtling), and a prioritized action checklist.

### **Goal 2: Educational Scaffolding and Strict Elo-Calibrated Persona Alignment**

The second goal is to demonstrate that supervised fine-tuning can enforce strict pedagogical calibration according to educational scaffolding principles (Vygotsky, 1978; Wood et al., 1976). Specifically, the model must dynamically alter both its semantic complexity and action-item density based on the player's Elo bracket:
- **Low-Elo Constraint**: For beginner profiles (<1000 Elo), the model must achieve a **100% compliance rate** on the "Rule of Three"—restricting its priority checklist to $\le 3$ blunt, high-impact macro directives, entirely suppressing micro-tactical jargon that would induce cognitive overload.
- **Mid-to-High-Elo Depth**: For intermediate and advanced profiles (>1000 Elo), the model must incorporate tech-upgrade sequencing, tactical kiting mechanics, and timing window projections without exceeding working memory limits.

### **Goal 3: Elimination of Domain Hallucinations (0% Systemic Error Rate)**

The third and most critical technical goal is the complete elimination of civilization technology-tree and unit counter hallucinations. The fine-tuned system must achieve:
- **0% Systemic Tech-Tree Violations**: Across benchmark evaluations featuring constrained civilizations (e.g., Aztecs, Mayans, Huns, Britons), the system must never present recommendations for units, technologies, or structures that are unavailable to that civilization or inaccessible in the current game age. This guarantee is achieved **systemically** through the neuro-symbolic combination of domain-adapted fine-tuning weights and an automated deterministic post-generation verifier (`hallucination_verifier.py`).
- **Tactical Counter Validity**: The recommended military compositions must demonstrate valid tactical effectiveness against observed opponent forces, verified against the mathematical ground-truth damage matrix of AoE2:DE.

### **Goal 4: Deterministic JSON Schema Compliance, Latency, and Statistical Verification**

The fourth goal is to achieve production-grade operational reliability necessary for live application deployment:
- **100% Structured Output Compliance**: Every model inference must parse cleanly against the predefined Pydantic JSON schema (`TacticalCoachResponse`) without missing keys, hallucinated attributes, conversational wrappers, or markdown syntax artifacts.
- **Sub-Second Inference Latency**: By eliminating multi-thousand-token in-context reference manuals and fine-tuning domain knowledge directly into model weights, total inference latency must remain under 1.0–1.5 seconds, ensuring recommendations remain tactically relevant in real time.
- **Rigorous Statistical Superiority over Baseline Models**: In formal benchmark comparisons against zero-shot transformer baselines (`gemini-1.5-flash`, `gpt-4o-mini`) across a suite of held-out test scenarios:
  - Categorical failure rates (tech-tree hallucination rate and schema failure rate) will be evaluated for statistical significance using **McNemar’s test for paired nominal data**.
  - Continuous metrics (inference latency in milliseconds and total prompt/completion token consumption) will be evaluated using the non-parametric **Wilcoxon signed-rank test**.
  - Action-item limit compliance ($\le 3$ items for low-Elo prompts) will be evaluated using **Fisher’s exact test**.

---

## **Initial Thoughts About How We Might Approach the Problem**

*Note: The methodologies outlined herein represent initial working hypotheses based on domain knowledge, cognitive load theory, and the current state of generative AI research (we will almost certainly change and refine this as we learn more through empirical experimentation across Milestones 2, 3, and 4).*

### **System Architectural Overview**

The planned architecture for `aoe2-coach` decouples the system into five modular subsystems: data ingestion, deterministic knowledge grounding, fine-tuning data synthesis, foundation model fine-tuning, and an interactive human-centered delivery interface.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                     AOE2-COACH SYSTEM ARCHITECTURE                          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  [ Match Telemetry Ingestion ]                                              │
│         │                                                                   │
│         ├──────────────┬───────────────────────────────┐                    │
│         │              │                               │                    │
│         ▼              ▼                               ▼                    │
│   (Tech Tree API) (Counter Matrix)        (Rate-Drain Economy Solver)       │
│   `tech_tree.py`  `counter_matrix.py`        `economy_solver.py`            │
│         │              │                               │                    │
│         └──────────────┼───────────────────────────────┘                    │
│                        │                                                    │
│                        ▼                                                    │
│         [ Deterministic Knowledge Grounding ]                               │
│                        │                                                    │
│                        ▼                                                    │
│         [ Supervised SFT Dataset Synthesis ]                                │
│           • Match State Vector -> Strict JSON Target                        │
│           • `train.jsonl` / `val.jsonl` (Stratified Sampling)               │
│                        │                                                    │
│                        ▼                                                    │
│         [ Hosted Fine-Tuned Transformer (Google Gemini 1.5 Flash) ]         │
│           • Weight-Encoded Tech-Tree Knowledge (Ouyang et al., 2022)        │
│           • Elo Persona Adaptation                                          │
│           • Deterministic JSON Emission                                     │
│                        │                                                    │
│                        ▼                                                    │
│         [ Verification & Hallucination Guardrail ]                          │
│           • Pydantic Schema Validator                                       │
│           • Automated Tech-Tree Unit Interceptor                            │
│                        │                                                    │
│                        ▼                                                    │
│         [ Streamlit Web Application Interface ]                             │
│           • Real-Time Interactive Coaching Dashboard                        │
│           • Side-by-Side Base vs. Fine-Tuned Comparator                     │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

### **1. Telemetry Ingestion and State Reconstruction**

The initial approach to game state ingestion involves extracting structured telemetry snapshots from public AoE2:DE recorded game files (`.aoe2record`) and real-time state emulators. 
- **Binary Parsing**: Using Rust-accelerated parser bindings (`aoe2rec-py` / `aoc-mgz`), match headers and binary operation streams are decoded into time-series game states sampled at critical inflection timestamps ($t \in \{5, 10, 15, 20, 25, 30\}$ minutes).
- **Simulated Fog-of-War**: A critical research consideration is partial observability. Replays contain total map state, but human players make decisions under incomplete information. The state ingestion module explicitly models player perspective field-of-view (FoV), maintaining an observation memory vector that logs only sighted enemy units and structures while incorporating an observation decay factor for stale intelligence.

### **2. Anchoring with Deterministic Domain Engines**

Rather than expecting a raw neural network to memorize arithmetic damage formulas and 45 distinct civilization graphs purely through probabilistic associations, the architecture grounds all training data generation in existing, deterministic Python rules engines:
- **Technology Tree Engine (`tech_tree.py`)**: A directed acyclic graph (DAG) representation of building prerequisites, age unlocks, and civilization-specific unit/technology exclusions across all 45 civilizations.
- **Combat Counter Matrix (`counter_matrix.py` & `damage_calculator.py`)**: A comprehensive mathematical model calculating exact base attacks, pierce armor values, and hidden bonus damage multipliers (e.g., Spearmen dealing $+15$ bonus damage against cavalry).
- **Rate-Drain Economy Optimizer (`economy_solver.py`)**: A deterministic continuous rate-balancing solver that computes instantaneous consumption rates ($\text{Cost} / \text{TrainTime} \times \text{BatchSize}$) across active production buildings, adds a farm reseeding wood coefficient, divides by task-specific gatherer rates, and applies an integer ceiling allocation to determine the exact gatherers needed on Food, Wood, Gold, and Stone.

### **3. Dataset Generation and Supervised Fine-Tuning Pipeline**

To train the generative coaching model, we will construct a high-fidelity synthetic supervised fine-tuning (SFT) dataset pairing match telemetry prompts with verified coaching completions (Ouyang et al., 2022).

#### *Training Data Formulation (`train.jsonl` / `val.jsonl`)*
Each training instance follows the standard conversational JSONL schema (supported natively by Google GenAI `TuningDataset` as well as standard chat completions). The training target is generated by running raw state vectors through the deterministic engines to obtain mathematically guaranteed counter-units and optimal villager targets, which are then structured into an Elo-calibrated JSON payload:

```json
{
  "messages": [
    {
      "role": "system",
      "content": "You are the Grandmaster AI Tactical Coach for Age of Empires II: Definitive Edition. Provide concise, Elo-calibrated, hallucination-free tactical advice strictly obeying civilization tech trees in JSON format."
    },
    {
      "role": "user",
      "content": "Match State:\nPlayer: Aztecs | Elo: 920 (Beginner) | Age: Castle Age (21:30)\nResources: Food: 150, Wood: 1200, Gold: 180, Stone: 100\nVillagers: Food: 8, Wood: 28, Gold: 6, Stone: 0\nSighted Enemy: 14 Frankish Knights, 2 Stables\nPlayer Military: 4 Crossbowmen"
    },
    {
      "role": "assistant",
      "content": "{\"primary_directive\":\"PIKEMAN & MONK DEFENSE\",\"coach_summary\":\"You are floating severe excess wood while Frankish knights are raiding. Aztecs have no cavalry—switch woodcutters to farms and mass Pikemen.\",\"elo_tier\":\"beginner\",\"military_plan\":{\"primary_unit_recommendation\":\"Pikeman\",\"secondary_unit_recommendation\":\"Monk\",\"production_building_instruction\":\"Build 2 additional Barracks (3 total)\",\"key_tech_priorities\":[\"Pikeman\",\"Chain Mail Armor\"],\"counter_explanation\":\"Pikemen deal massive bonus damage against Frank cavalry with zero gold cost.\",\"micro_positioning_tip\":\"Keep Pikemen stationed on top of your woodline and farms; do not chase Knights in open fields.\"},\"economic_plan\":{\"problem_diagnosis\":\"Severe wood float (1200 wood) with food starvation.\",\"immediate_action\":\"Pull 10 lumberjacks immediately to seed farms around your Town Center.\",\"target_villager_allocation\":{\"food\":18,\"wood\":18,\"gold\":8,\"stone\":0},\"macro_tip\":\"Spend your wood as soon as it crosses 200 by building farms or production buildings.\"},\"timing_plan\":{\"posture\":\"Defensive Turtling\",\"attack_window\":\"Next 5 minutes\",\"threat_alert\":\"Frank Castle Age cavalry power spike active\",\"strategic_spike_reasoning\":\"Defend until Pikeman numbers reach 20+, then add Monks to convert forward Knights.\"},\"priority_checklist\":[\"1. Move 10 lumberjacks to build 10 farms\",\"2. Construct 2 Barracks immediately\",\"3. Queue continuous Pikemen production\"]}"
    }
  ]
}
```

#### *Stratified Sampling and Training Infrastructure*
In strict alignment with the course requirement that the architecture be transformer-based:
- **Foundation Architecture**: Google `gemini-1.5-flash` will serve as the base model (Gemini Team, 2024), satisfying the transformer-based architectural requirement while delivering high parameter efficiency, low inference latency, and native structured JSON output support.
- **Stratified & Adversarial Sampling**: Recognizing that a naive uniform sampling across 45 civilizations would provide only ~4 to 6 examples per civilization in a 250-sample dataset, the dataset generation pipeline will employ **stratified adversarial weighting**. Scenarios involving high-hallucination edge cases—specifically Mesoamerican civilizations (Aztecs, Mayans, Incas lacking cavalry), nomadic civilizations (Huns lacking houses), and asymmetric cavalry specialists (Gurjaras)—will be intentionally oversampled to ensure solid parameter adaptation.
- **Hosted Serverless Fine-Tuning (Google Cloud)**: Training will be executed using the Google GenAI fine-tuning API (Google AI Studio / Vertex AI) managed entirely through an end-to-end Python workflow in a Jupyter Notebook (`notebooks/Milestone3_FineTuning.ipynb`). This cloud-hosted approach ensures zero local VRAM or GPU overhead on the host machine running the game, eliminates the complex local quantization dependencies of PEFT/LoRA, and incurs \$0 standby hosting costs.
- **Optimization & Loss Tracking**: Hyperparameters will be initialized at 3 training epochs with a learning rate of 0.001 and batch size of 4. Loss convergence snapshots will be retrieved from the tuning task metadata via the `google-genai` SDK and visualized using Matplotlib.

### **4. Post-Generation Verification and Safety Guardrail**

To guarantee zero-defect operational safety during live gameplay, the pipeline incorporates an automated verification layer (`hallucination_verifier.py`):
1. **Pydantic Validation**: The raw model output is deserialized into a typed schema. If a parsing failure or missing-key error occurs, an immediate repair prompt is triggered.
2. **Deterministic Constraint Guardrail**: The recommended units and technologies are checked against the player's civilization node in `tech_tree.py`. If a forbidden unit is detected (e.g., Knights for Aztecs), the system automatically intercepts the response and falls back to a deterministic template generated by `fallback_engine.py`.

### **5. Interactive Delivery Interface**

For Milestone 4, the system will culminate in a high-performance Streamlit dashboard (`streamlit_app.py`):
- **Interactive Match Setup**: Sliders and visual dropdowns allowing users to configure civilization matchups, player Elo rating, game age, and current timestamps.
- **Live Telemetry Sliders**: Resource stockpile inputs and villager allocation controls that immediately simulate floating resources and economic deficits.
- **Sighted Unit Selectors**: Visual multi-select controls representing enemy forces spotted through the fog-of-war.
- **Tactical Directive Dashboard**: A structured visual presentation displaying high-urgency banner alerts, unit production badges, villager reallocation tables, and the Elo-calibrated priority checklist.
- **Side-by-Side Model Comparator**: A live diagnostic feature allowing evaluators to compare the output of the zero-shot base foundation model directly against the fine-tuned model on identical match states, rendering hallucinations and formatting failures immediately apparent.

### **Anticipated Methodological Evolutions and Learning Trajectory**

As noted in the project mandate, initial thoughts about problem formulation almost certainly evolve as empirical insights are gathered. Key dimensions anticipated to shift during upcoming milestones include:

1. **State Vector Sparsity and Partial Scouting Representation**: In early iterations, match telemetry assumes relatively clean, structured inputs. In live competitive gameplay, however, scouting data is frequently noisy, incomplete, or absent. In Milestone 2 (Prompt Experiments), we anticipate discovering that base models struggle when enemy unit counts are unknown. The prompt structure may need to incorporate probabilistic language or explicit "scouting priority" directives (e.g., *"Scout opponent forward radius before committing to anti-cavalry production"*).
2. **Trade-Offs in Action Density vs. Token Latency**: While our current hypothesis suggests beginner players need exactly $\le 3$ action items, user testing may reveal that certain complex transitions require secondary prerequisites (e.g., researching a Blacksmith before building a Siege Workshop). Balancing brevity against tactical completeness will be empirically calibrated through the five benchmark experiments in Milestone 2.
3. **Training Dataset Scale vs. Overfitting**: Current dataset targets anticipate generating 200 to 300 highly verified synthetic scenarios. Empirical training in Milestone 3 will reveal whether this volume suffices to eliminate tech-tree hallucinations across all 45 civilizations, or whether active data augmentation focusing specifically on edge-case civilizations (e.g., Mesoamericans, Huns, Gurjaras) is necessary to avoid catastrophic forgetting or narrow memorization.
4. **Structured Outputs and Constrained Decoding**: Google's GenAI and Gemini APIs support typed schema definitions (`response_schema`) and constrained decoding. In Milestones 2 and 3, we will evaluate whether native schema enforcement completely eliminates the need for post-hoc Pydantic repair prompts, thereby minimizing round-trip coaching latency during live matches.

---

## **Conclusion**

Real-time strategy games provide a rigorous testing ground for evaluating the real-world utility of generative artificial intelligence under strict cognitive, temporal, and ontological constraints. Off-the-shelf foundation models fall short in this domain, generating hallucinations, verbose uncalibrated prose, and unreliable schemas. By integrating deterministic game rules with hosted supervised fine-tuning of the transformer-based `gemini-1.5-flash` on Google Cloud, the `aoe2-coach` project offers a principled solution that converts complex match telemetry into real-time, skill-adapted tactical directives without imposing hardware contention on the host system. This Milestone 1 paper establishes the theoretical foundation, academic goals, and initial engineering roadmap for the project, laying the groundwork for prompt experimentation in Milestone 2, model fine-tuning in Milestone 3, and interactive application delivery in Milestone 4.

---

<br>

# **References**

<div style="padding-left: 2em; text-indent: -2em;">

Achiam, J., Adler, S., Agarwal, S., Ahmad, L., Akkaya, I., Aleman, F. L., Almeida, D., Altenschmidt, J., Altman, S., Anadkat, S., Avila, R., Babuschkin, I., Balaji, S., Balcom, V., Baltescu, P., Bao, H., Bavarian, M., Belgum, R., Bello, I., … Zoph, B. (2023). *GPT-4 technical report* (arXiv:2303.08774). arXiv. https://doi.org/10.48550/arXiv.2303.08774

Baddeley, A. (1992). Working memory. *Science*, *255*(5044), 556–559. https://doi.org/10.1126/science.1736359

Baddeley, A. (2000). The episodic buffer: A new component of working memory? *Trends in Cognitive Sciences*, *4*(11), 417–423. https://doi.org/10.1016/S1364-6613(00)01538-2

Brown, T., Mann, B., Ryder, N., Subbiah, M., Kaplan, J. D., Dhariwal, P., Neelakantan, A., Shyam, P., Sastry, G., Askell, A., Agarwal, S., Herbert-Voss, A., Krueger, G., Henighan, T., Child, R., Ramesh, A., Ziegler, D., Wu, J., Winter, C., … Amodei, D. (2020). Language models are few-shot learners. *Advances in Neural Information Processing Systems*, *33*, 1877–1901. https://proceedings.neurips.cc/paper/2020/hash/1457c0d6bfcb4967418bfb8ac142f64a-Abstract.html

Buro, M. (2003). Real-time strategy games: A new AI research challenge. In *Proceedings of the 18th International Joint Conference on Artificial Intelligence (IJCAI-03)* (pp. 1534–1535). Morgan Kaufmann.

Gemini Team, Google. (2024). *Gemini 1.5: Unlocking multimodal understanding across millions of tokens of context* (arXiv:2403.05530). arXiv. https://doi.org/10.48550/arXiv.2403.05530

Ontañón, S., Synnaeve, G., Uriarte, A., Richoux, F., Churchill, D., & Preuss, M. (2013). A survey of real-time strategy game AI research and competition in StarCraft. *IEEE Transactions on Computational Intelligence and AI in Games*, *5*(4), 293–311. https://doi.org/10.1109/TCIAIG.2013.2286295

Ouyang, L., Wu, J., Jiang, X., Almeida, D., Wainwright, C., Mishkin, P., Zhang, C., Agarwal, S., Slama, K., Ray, A., Schulman, J., Hilton, J., Kelton, F., Miller, L., Simens, M., Askell, A., Welinder, P., Christiano, P., Leike, J., & Lowe, R. (2022). Training language models to follow instructions with human feedback. *Advances in Neural Information Processing Systems*, *35*, 27730–27744. https://proceedings.neurips.cc/paper_files/paper/2022/hash/b1efde53be364a73914f58805a001731-Abstract.html

Silver, D., Hubert, T., Schrittwieser, J., Antonoglou, I., Lai, M., Guez, A., Lanctot, M., Sifre, L., Dhar, P., Lillicrap, T., Graepel, T., Hassabis, D., & Bowling, M. (2018). A general reinforcement learning algorithm that masters chess, shogi, and Go through self-play. *Science*, *362*(6419), 1140–1144. https://doi.org/10.1126/science.aar6404

Staal, M. A. (2004). *Stress, cognition, and human performance: A literature review and conceptual framework* (NASA/TM-2004-212824). National Aeronautics and Space Administration, Ames Research Center. https://ntrs.nasa.gov/citations/20060000305

Sweller, J. (1988). Cognitive load during problem solving: Effects on learning. *Cognitive Science*, *12*(2), 257–285. https://doi.org/10.1207/s15516709cog1202_4

Sweller, J. (2011). Cognitive load theory. *Psychology of Learning and Motivation*, *55*, 37–76. https://doi.org/10.1016/B978-0-12-387690-4.00002-8

Vinyals, O., Babuschkin, I., Czarnecki, W. M., Mathieu, M., Dudzik, A., Chung, J., Choi, D. H., Powell, R., Ewalds, T., Georgiev, P., Oh, J., Horgan, D., Kroiss, M., Esslinger, I., Grefenstette, E., Rae, J., Barekatain, M., Liang, X., Gilbert, T., … Hassabis, D. (2019). Grandmaster level in StarCraft II using multi-agent reinforcement learning. *Nature*, *575*(7782), 350–354. https://doi.org/10.1038/s41586-019-1724-z

Vygotsky, L. S. (1978). *Mind in society: The development of higher psychological processes* (M. Cole, V. John-Steiner, S. Scribner, & E. Souberman, Eds.). Harvard University Press.

Wood, D., Bruner, J. S., & Ross, G. (1976). The role of tutoring in problem solving. *Journal of Child Psychology and Psychiatry*, *17*(2), 89–100. https://doi.org/10.1111/j.1469-7610.1976.tb00381.x

</div>
