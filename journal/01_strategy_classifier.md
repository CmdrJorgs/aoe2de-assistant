# 01_strategy_classifier

## Question / hypothesis

Can a Random Forest / Gradient Boosting classifier accurately predict canonical military unit compositions from encoded AoE2 match states and opponent armies?

## Motivation

- **Sourcing strategy:** user
- **Source(s):** AoE2 tactical decision engine core pipeline
- **Why this matters:** High-ELO players must proactively counter-comp based on sighted enemy units and civ affinities.

## Method

- **Files touched:** `aoe2_coach/models/strategy_classifier.py`, `experiments/01_strategy_classifier.py`
- **Change versus baseline:** Initial Skore pipeline evaluation with 3-fold cross validation.
- **Cross-validation:** KFold(n_splits=3, shuffle=True, random_state=42)
- **Out of scope for this experiment:** Hyperparameter tuning.

## Risks / things that could invalidate the result

- Synthetic dataset distributions may oversimplify messy multi-unit late game compositions.

## Status

- **State:** done
- **Approved by user on:** 2026-08-28
- **Headline result:** Accuracy 1.00 ± 0.00 across 3 folds (Log Loss 0.14)
- **Implication for next iteration:** Model shows strong discrimination on composition counters.
