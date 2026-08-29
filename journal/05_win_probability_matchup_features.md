# 05_win_probability_matchup_features

<!--
Design note for experiments/05_win_probability_matchup_features.py (same stem, 1:1 with the script).
-->

## Question / hypothesis

Will engineering direct civilization matchup interaction terms (affinity deltas and rock-paper-scissors counter advantages) and economic raiding efficiency / kill rate features lift the Win Probability estimator's ROC-AUC from baseline 0.66 to >0.75?

## Motivation

- **Sourcing strategy:** user
- **Source(s):** User request following experiment `02_win_probability` audit findings.
- **Why this matters:** Win probability in AoE2 is heavily driven by civilization counter-dynamics (e.g., cavalry civs punishing archer civs on open maps) and economic disruptions (villager kills / raiding pressure).

## Method

- **Files touched:**
  - `aoe2_coach/models/feature_encoder.py`: Add civ matchup interaction terms and economic kill rate features.
  - `aoe2_coach/models/train_pipeline.py`: Include synthetic simulation and dataset generation for eco kill momentum.
  - `experiments/05_win_probability_matchup_features.py`: Execute Skore evaluation and persist report.
  - `tests/smoke/test_05_win_probability_matchup_features.py`: Smoke test feature encoding and estimator inference.
  - `audit/05_win_probability_matchup_features.py`: Skore report audit.
- **Change versus baseline (`02_win_probability`):**
  - Add 5 civ affinity deltas (`cav_matchup_delta`, `arch_matchup_delta`, `inf_matchup_delta`, `siege_matchup_delta`, `monk_matchup_delta`).
  - Add 3 archetype cross-counter interaction terms (`cav_vs_opp_arch_interaction`, `arch_vs_opp_inf_interaction`, `inf_vs_opp_cav_interaction`).
  - Add economic raiding kill rate & momentum features (`eco_kill_rate_est`, `military_build_velocity`, `vill_pacing_efficiency`).
- **Cross-validation:** KFold(n_splits=3, shuffle=True, random_state=42)
- **Out of scope for this experiment:** Hyperparameter grid search / tuning of the Random Forest.

## Risks / things that could invalidate the result

- Risk of multicollinearity between civ affinity deltas and raw civ affinities (`SKD008` check).
- Risk of over-weighting early villager kills if game time is short.

## Status

- **State:** done
- **Approved by user on:** 2026-08-28
- **Headline result:** Accuracy 0.974 ± 0.015, ROC-AUC 0.978 ± 0.021, Brier Score 0.018 (lifted from baseline AUC 0.665)
- **Implication for next iteration:** Civ matchup interaction deltas and raiding eco kill velocity provide decisive predictive power for match win estimation. Model is ready for ONNX export.
