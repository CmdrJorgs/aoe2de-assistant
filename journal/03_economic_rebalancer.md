# 03_economic_rebalancer

## Question / hypothesis

Can a multi-target regressor learn optimal high-ELO villager gatherer distributions across Food, Wood, Gold, and Stone?

## Motivation

- **Sourcing strategy:** user
- **Source(s):** AoE2 Macroeconomic rebalancer
- **Why this matters:** Unbalanced gatherer allocations cause floating resources and delayed age-up timings.

## Method

- **Files touched:** `aoe2_coach/models/economic_rebalancer.py`, `experiments/03_economic_rebalancer.py`
- **Change versus baseline:** Initial Skore pipeline evaluation with 3-fold cross validation.
- **Cross-validation:** KFold(n_splits=3, shuffle=True, random_state=42)
- **Out of scope for this experiment:** Market buy/sell optimization.

## Risks / things that could invalidate the result

- Floating wood during farm transitions must be accounted for.

## Status

- **State:** done
- **Approved by user on:** 2026-08-28
- **Headline result:** R² 0.999 ± 0.001, MAE 0.0006
- **Implication for next iteration:** Model fits target macro distributions with high precision.
