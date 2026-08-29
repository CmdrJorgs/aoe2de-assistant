# 02_win_probability

## Question / hypothesis

Can an ensemble classifier estimate real-time win probability $P(\text{Win} \mid \text{State})$ from economic balance, military headcounts, and civ match dynamics?

## Motivation

- **Sourcing strategy:** user
- **Source(s):** AoE2 live match assessment engine
- **Why this matters:** Players need objective gauge of game state momentum to decide when to push or retreat.

## Method

- **Files touched:** `aoe2_coach/models/win_probability_estimator.py`, `experiments/02_win_probability.py`
- **Change versus baseline:** Initial Skore pipeline evaluation with 3-fold cross validation.
- **Cross-validation:** KFold(n_splits=3, shuffle=True, random_state=42)
- **Out of scope for this experiment:** Calibration curve adjustment.

## Risks / things that could invalidate the result

- Non-linear comebacks in AoE2 (e.g. Castle drops, Relic victories) introduce inherent variance.

## Status

- **State:** done
- **Approved by user on:** 2026-08-28
- **Headline result:** Accuracy 0.69 ± 0.04, ROC-AUC 0.63 ± 0.04, Brier Score 0.22
- **Implication for next iteration:** Enrich with civ matchup interaction features and eco kill momentum.
