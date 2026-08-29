# JOURNAL

## Status

- **Project / dataset:** Age of Empires II: DE Match & Tactical State Modelling
- **Goal:** Predict military compositions, win probabilities, economic allocations, and tactical combat stances in real-time (<20ms).
- **Last experiment:** 05_win_probability_matchup_features — done
- **Last result:** ROC-AUC 0.978 ± 0.021 (lifted from baseline 0.665)

- **Workspace decisions** (immutable unless the user pivots):
  - tabular library: pandas — recorded: 2026-08-28
  - env manager: uv — recorded: 2026-08-28
  - agent feature: installed — recorded: 2026-08-28
  - optional features: none — recorded: 2026-08-28
  - package name (`src/<pkg>/`): aoe2_coach — recorded: 2026-08-28
  - skore mode: local — recorded: 2026-08-28
  - skore hub workspace: n/a — recorded: 2026-08-28
  - skore mlflow tracking uri: n/a — recorded: 2026-08-28
  - CV splitter family: KFold — recorded: 2026-08-28

## Data understanding (EDA)

- **Status:** done — 2026-08-28
- **Summary:** Multi-civ tactical game state snapshots (45 civs, Feudal to Imperial age, military unit counts, tech counters, resource stockpiles, and villager distributions).
- **Report:** [data/eda.md](../data/eda.md)

## History

| Stem | Intent (one line) | Status | Headline result | Design note |
|---|---|---|---|---|
| `01_strategy_classifier` | Multiclass military counter composition prediction | done | Accuracy 1.00 ± 0.00, ROC-AUC macro 1.00 ± 0.00 | [design note](01_strategy_classifier.md) |
| `02_win_probability` | Binary win/loss probability estimation from game features | done | Accuracy 0.68 ± 0.03, ROC-AUC 0.66 ± 0.04 | [design note](02_win_probability.md) |
| `03_economic_rebalancer` | Multi-resource villager gatherer allocation prediction | done | R² 0.999 ± 0.001, MAE 0.0006 | [design note](03_economic_rebalancer.md) |
| `04_stance_timing` | Multiclass tactical combat stance classification | done | Accuracy 0.94 ± 0.01, ROC-AUC macro 0.91 | [design note](04_stance_timing.md) |
| `05_win_probability_matchup_features` | Win probability with civ interaction terms & eco kill velocity | done | Accuracy 0.974 ± 0.015, ROC-AUC 0.978 ± 0.021 | [design note](05_win_probability_matchup_features.md) |

## Backlog

| # | Item | Source |
|---|---|---|
| B1 | Benchmark LightGBM vs RandomForest on Stance timing | `my-pick:04_stance_timing` |
| B2 | Evaluate calibration curve (CalibratedClassifierCV) on Win Probability | `skore:05_win_probability_matchup_features` |
