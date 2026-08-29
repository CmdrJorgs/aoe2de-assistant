import numpy as np
import pandas as pd
import skore
from sklearn.model_selection import KFold
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.strategy_classifier import StrategyClassifier, map_label_to_canonical_comp
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES

print("Generating synthetic dataset...")
df = generate_augmented_training_dataset(num_synthetic_samples=500)
encoder = FeatureEncoder()
X = encoder.encode_dataframe(df)

print("1. Testing StrategyClassifier...")
strat_clf_wrapper = StrategyClassifier()
y_comp = np.array([strat_clf_wrapper.label_encoder.transform([map_label_to_canonical_comp(lbl)])[0] for lbl in df["label_primary_comp"].fillna("knight_line")])
rep_strat = skore.evaluate(strat_clf_wrapper.comp_model, X, y_comp, splitter=KFold(n_splits=3, shuffle=True, random_state=42))
print("StrategyClassifier evaluated successfully.")
print("Checks:\n", rep_strat.checks.summarize().frame())
print("Metrics:\n", rep_strat.metrics.summarize().frame())

print("\n2. Testing WinProbabilityEstimator...")
y_win = df["label_winner"].astype(int).values
win_est_wrapper = WinProbabilityEstimator()
rep_win = skore.evaluate(win_est_wrapper.model, X, y_win, splitter=KFold(n_splits=3, shuffle=True, random_state=42))
print("WinProbability evaluated successfully.")
print("Checks:\n", rep_win.checks.summarize().frame())
print("Metrics:\n", rep_win.metrics.summarize().frame())

print("\n3. Testing StanceTimingPredictor...")
stance_wrapper = StanceTimingPredictor()
y_stance = np.array([stance_wrapper.label_encoder.transform([s if s in STANCE_CLASSES else "FORWARD_PRESSURE"])[0] for s in df["label_stance"].fillna("FORWARD_PRESSURE")])
rep_stance = skore.evaluate(stance_wrapper.model, X, y_stance, splitter=KFold(n_splits=3, shuffle=True, random_state=42))
print("StanceTiming evaluated successfully.")
print("Checks:\n", rep_stance.checks.summarize().frame())
print("Metrics:\n", rep_stance.metrics.summarize().frame())

print("\n4. Testing EconomicRebalancer (Single target or Multi-output)...")
# Note: Economic rebalancer predicts 4 targets [pct_f, pct_w, pct_g, pct_s]
# Let's test food ratio or multi-output with skore
vills_tot = np.maximum(1, df["player_vills_total"].values)
y_food = (df["player_vills_food"].values / vills_tot).astype(np.float32)
eco_wrapper = EconomicRebalancer()
rep_eco = skore.evaluate(eco_wrapper.model, X, y_food, splitter=KFold(n_splits=3, shuffle=True, random_state=42))
print("EconomicRebalancer evaluated successfully.")
print("Checks:\n", rep_eco.checks.summarize().frame())
print("Metrics:\n", rep_eco.metrics.summarize().frame())

print("\nALL 4 MODELS EVALUATED WITH SKORE SUCCESSFULLY!")
