# 04_stance_timing

## Question / hypothesis

Can a classifier reliably detect tactical stances (Aggressive, Forward Pressure, Defensive Turtling, Fast Imperial Boom, Relic Control) from game progression signals?

## Motivation

- **Sourcing strategy:** user
- **Source(s):** AoE2 tactical timing advisor
- **Why this matters:** Knowing when to attack vs boom is critical for closing out matches.

## Method

- **Files touched:** `aoe2_coach/models/stance_timing_predictor.py`, `experiments/04_stance_timing.py`
- **Change versus baseline:** Initial Skore pipeline evaluation with 3-fold cross validation.
- **Cross-validation:** KFold(n_splits=3, shuffle=True, random_state=42)
- **Out of scope for this experiment:** Map-specific elevation features.

## Risks / things that could invalidate the result

- Minor class imbalance on rare stances (e.g. Relic Hill Control).

## Status

- **State:** done
- **Approved by user on:** 2026-08-28
- **Headline result:** Accuracy 0.94 ± 0.01, ROC-AUC macro 0.91
- **Implication for next iteration:** Validated robust baseline; next step is testing LightGBM vs Random Forest.
