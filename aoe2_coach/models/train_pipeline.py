"""
AoE2 Model Training & ONNX Export Pipeline:
Trains Strategy Classifier, Value Estimator, Economic Rebalancer, and Stance Predictor.
Exports validated models to ONNX for sub-20ms inference.
"""

import os
import glob
import logging
import argparse
from typing import Dict, List, Optional, Tuple, Any, Union
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, roc_auc_score, mean_absolute_error, classification_report

from aoe2_coach.schemas.game_constants import CIVILIZATIONS, Age
from aoe2_coach.pipeline.dataset_exporter import DatasetExporter
from aoe2_coach.models.feature_encoder import FeatureEncoder, CIV_ARCHETYPES
from aoe2_coach.models.strategy_classifier import (
    StrategyClassifier,
    COMPOSITION_CLASSES,
    map_label_to_canonical_comp,
)
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer, HIGH_ELO_RATIOS
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES
from aoe2_coach.models.onnx_exporter import ONNXExporter

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def generate_augmented_training_dataset(
    base_df: Optional[pd.DataFrame] = None,
    num_synthetic_samples: int = 2500,
) -> pd.DataFrame:
    """
    Generate a diverse, comprehensive training dataset covering all 45 civilizations,
    all ages (Feudal, Castle, Imp), and tactical counter-compositions.
    """
    records: List[Dict[str, Any]] = []

    if base_df is not None and not base_df.empty:
        records.extend(base_df.to_dict(orient="records"))

    logger.info(f"Augmenting dataset with {num_synthetic_samples} multi-civ high-ELO game scenarios...")

    civ_names = list(CIVILIZATIONS.values())
    np.random.seed(42)

    for i in range(num_synthetic_samples):
        p_civ = np.random.choice(civ_names)
        opp_civ = np.random.choice(civ_names)
        p_age = int(np.random.choice([2, 3, 4], p=[0.25, 0.55, 0.20]))
        opp_age = int(np.random.choice([p_age - 1, p_age, min(4, p_age + 1)], p=[0.15, 0.70, 0.15]))
        p_age = max(1, min(4, p_age))
        opp_age = max(1, min(4, opp_age))

        t_sec = int(np.random.normal(loc=p_age * 480, scale=120))
        t_sec = max(300, min(2400, t_sec))
        elo = int(np.random.normal(loc=1400, scale=250))

        # Civ archetype affinities
        p_aff = CIV_ARCHETYPES.get(p_civ.lower(), {"cavalry": 0.5, "archer": 0.5, "infantry": 0.5, "siege": 0.5, "monk": 0.5})

        # Determine logical winning composition
        opp_sighted_cav = int(np.random.poisson(lam=4 if p_age >= 3 else 2))
        opp_sighted_arch = int(np.random.poisson(lam=6 if p_age >= 3 else 3))
        opp_sighted_inf = int(np.random.poisson(lam=3))

        # Composition selection based on civ strengths and opponent army
        if p_aff["cavalry"] >= 0.9 and opp_sighted_cav < 6:
            label_comp = "knight_line" if p_age >= 3 else "scout_line"
            label_unit = "knight" if p_age >= 3 else "scout_cavalry"
            label_bld = "stable"
            label_tech = "scale_barding_armor"
        elif p_aff["archer"] >= 0.9 or opp_sighted_inf > 5:
            label_comp = "crossbow_line" if p_age >= 3 else "archer"
            label_unit = "crossbowman" if p_age >= 3 else "archer"
            label_bld = "archery_range"
            label_tech = "bodkin_arrow"
        elif opp_sighted_cav >= 6:
            label_comp = "pike_line" if p_aff["cavalry"] < 0.8 else "camel_line"
            label_unit = "pikeman" if label_comp == "pike_line" else "camel_rider"
            label_bld = "barracks" if label_comp == "pike_line" else "stable"
            label_tech = "scale_mail_armor"
        elif opp_sighted_arch >= 8:
            label_comp = "skirm_line"
            label_unit = "elite_skirmisher" if p_age >= 3 else "skirmisher"
            label_bld = "archery_range"
            label_tech = "leather_archer_armor"
        elif p_aff["infantry"] >= 0.9:
            label_comp = "champion_line"
            label_unit = "long_swordsman" if p_age == 3 else "champion"
            label_bld = "barracks"
            label_tech = "iron_casting"
        else:
            label_comp = "knight_line" if p_age >= 3 else "crossbow_line"
            label_unit = "knight" if label_comp == "knight_line" else "crossbowman"
            label_bld = "stable" if label_comp == "knight_line" else "archery_range"
            label_tech = "bloodlines"

        # Villagers count
        tot_vills = int(min(130, max(18, (t_sec / 25.0) + np.random.normal(0, 3))))
        ratios = HIGH_ELO_RATIOS.get(label_comp, {"food": 0.40, "wood": 0.35, "gold": 0.20, "stone": 0.05})

        vills_f = int(tot_vills * ratios["food"])
        vills_w = int(tot_vills * ratios["wood"])
        vills_g = int(tot_vills * ratios["gold"])
        vills_s = tot_vills - (vills_f + vills_w + vills_g)

        # Stockpile
        food_stock = int(np.random.exponential(scale=350))
        wood_stock = int(np.random.exponential(scale=350))
        gold_stock = int(np.random.exponential(scale=200))
        stone_stock = int(np.random.exponential(scale=100))

        # Win probability conditions with civ matchup synergy and eco kills
        opp_aff = CIV_ARCHETYPES.get(opp_civ.lower(), {"cavalry": 0.5, "archer": 0.5, "infantry": 0.5, "siege": 0.5, "monk": 0.5})
        civ_synergy = (
            (p_aff["cavalry"] * opp_aff["archer"])
            + (p_aff["archer"] * opp_aff["infantry"])
            + (p_aff["infantry"] * opp_aff["cavalry"])
            - (opp_aff["cavalry"] * p_aff["archer"])
            - (opp_aff["archer"] * p_aff["infantry"])
            - (opp_aff["infantry"] * p_aff["cavalry"])
        )
        mil_count = int(np.random.poisson(lam=max(2, tot_vills * 0.4)))
        opp_mil_total = opp_sighted_cav + opp_sighted_arch + opp_sighted_inf
        eco_lead = float(tot_vills - (t_sec / 28.0))
        mil_lead = float(mil_count - opp_mil_total)
        eco_kills = int(max(0, np.random.poisson(lam=max(0.2, mil_lead * 0.35 + 1.2 if mil_lead > 0 else 0.4))))
        eco_kill_rate = eco_kills / max(1.0, t_sec / 60.0)

        win_score = (eco_lead * 0.35) + (mil_lead * 0.40) + (civ_synergy * 1.5) + (eco_kill_rate * 2.0) + ((elo - 1400.0) / 400.0) + np.random.normal(0, 0.75)
        is_winner = bool(win_score > 0.0)

        # Tactical Stance Label
        if mil_count > opp_mil_total + 6 and p_age >= 3:
            stance_label = "ALL_IN_AGGRESSION"
        elif mil_count >= opp_mil_total:
            stance_label = "FORWARD_PRESSURE"
        elif opp_mil_total > mil_count + 5:
            stance_label = "DEFENSIVE_TURTLING"
        elif tot_vills > 60 and p_age == 3:
            stance_label = "FAST_IMPERIAL_BOOM"
        else:
            stance_label = "RELIC_HILL_CONTROL"

        row = {
            "match_id": f"syn_{i:05d}",
            "patch_version": "101.102.x",
            "timestamp_sec": t_sec,
            "map_type": "Arabia",
            "player_civ_id": 1,
            "player_civ_name": p_civ,
            "player_elo": elo,
            "player_age": p_age,
            "player_food": food_stock,
            "player_wood": wood_stock,
            "player_gold": gold_stock,
            "player_stone": stone_stock,
            "player_vills_total": tot_vills,
            "player_vills_food": vills_f,
            "player_vills_wood": vills_w,
            "player_vills_gold": vills_g,
            "player_vills_stone": vills_s,
            "player_military_total": mil_count,
            "player_tech_count": p_age * 3,
            "opponent_civ_id": 2,
            "opponent_civ_name": opp_civ,
            "opponent_estimated_age": opp_age,
            "opponent_sighted_units_count": opp_mil_total,
            "opponent_sighted_buildings_count": 3,
            "label_winner": is_winner,
            "label_next_unit": label_unit,
            "label_next_tech": label_tech,
            "label_next_building": label_bld,
            "label_primary_comp": label_comp,
            "label_stance": stance_label,
            "opp_sighted_cavalry": opp_sighted_cav,
            "opp_sighted_archers": opp_sighted_arch,
            "opp_sighted_infantry": opp_sighted_inf,
            "eco_kill_rate": eco_kill_rate,
            "opp_vills_killed_est": eco_kills,
        }
        records.append(row)

    return pd.DataFrame(records)


def run_training_pipeline(
    replays_dir: str = "data/raw",
    processed_parquet: str = "data/processed/snapshots.parquet",
    artifacts_dir: str = "aoe2_coach/models/artifacts",
    max_replays_to_parse: int = 40,
) -> Dict[str, Any]:
    """
    End-to-end training pipeline:
    1. Parse batch replays (if available) into snapshots Parquet.
    2. Encode features.
    3. Train Strategy Classifier, Win Probability Estimator, Economic Rebalancer, Stance Predictor.
    4. Validate on holdout test split.
    5. Export to ONNX.
    """
    logger.info("=== Commencing Phase 3 Machine Learning Training Pipeline ===")

    # 1. Ingest Replays / Snapshots
    base_df = None
    if os.path.exists(processed_parquet):
        logger.info(f"Loading existing parquet dataset from {processed_parquet}...")
        base_df = pd.read_parquet(processed_parquet)
    elif os.path.exists(replays_dir):
        raw_files = glob.glob(os.path.join(replays_dir, "*.aoe2record"))[:max_replays_to_parse]
        if raw_files:
            logger.info(f"Parsing {len(raw_files)} replays to Parquet...")
            exporter = DatasetExporter(output_dir=os.path.dirname(processed_parquet))
            stats = exporter.process_replay_batch(raw_files, processed_parquet, max_workers=4)
            logger.info(f"Processed {stats.total_snapshots} snapshots from replays.")
            if os.path.exists(processed_parquet):
                base_df = pd.read_parquet(processed_parquet)

    # 2. Augment dataset
    df = generate_augmented_training_dataset(base_df=base_df, num_synthetic_samples=3000)
    logger.info(f"Total training records assembled: {len(df)}")

    # 3. Feature Encoding
    encoder = FeatureEncoder()
    X = encoder.encode_dataframe(df)
    logger.info(f"Encoded feature matrix shape: {X.shape} (Features: {encoder.num_features})")

    # Extract Target Labels
    y_comp = [map_label_to_canonical_comp(lbl) for lbl in df["label_primary_comp"].fillna("knight_line")]
    y_win = df["label_winner"].astype(bool).values

    # Economic ratios target: [pct_f, pct_w, pct_g, pct_s]
    vills_tot = np.maximum(1, df["player_vills_total"].values)
    Y_eco_ratios = np.column_stack([
        df["player_vills_food"].values / vills_tot,
        df["player_vills_wood"].values / vills_tot,
        df["player_vills_gold"].values / vills_tot,
        df["player_vills_stone"].values / vills_tot,
    ]).astype(np.float32)

    # Stance labels
    if "label_stance" not in df.columns:
        y_stance = ["FORWARD_PRESSURE"] * len(df)
    else:
        y_stance = df["label_stance"].fillna("FORWARD_PRESSURE").astype(str).tolist()
    # Ensure all labels in y_stance are valid classes
    y_stance = [s if s in STANCE_CLASSES else "FORWARD_PRESSURE" for s in y_stance]

    # Train / Test Split
    indices = np.arange(len(X))
    train_idx, test_idx = train_test_split(indices, test_size=0.20, random_state=42, stratify=y_comp)

    X_train, X_test = X[train_idx], X[test_idx]
    y_comp_train = [y_comp[i] for i in train_idx]
    y_comp_test = [y_comp[i] for i in test_idx]
    y_win_train, y_win_test = y_win[train_idx], y_win[test_idx]
    Y_eco_train, Y_eco_test = Y_eco_ratios[train_idx], Y_eco_ratios[test_idx]
    y_stance_train = [y_stance[i] for i in train_idx]
    y_stance_test = [y_stance[i] for i in test_idx]

    # 4. Train Models
    logger.info("--- Training Strategy Classifier ---")
    strategy_clf = StrategyClassifier()
    strategy_clf.fit(X_train, y_comp_train)
    pred_comp_test = [strategy_clf.label_encoder.classes_[i] for i in np.argmax(strategy_clf.predict_proba(X_test), axis=1)]
    strat_acc = accuracy_score(y_comp_test, pred_comp_test)
    logger.info(f"Strategy Classifier Test Accuracy: {round(strat_acc * 100, 2)}%")

    logger.info("--- Training Win Probability Estimator ---")
    win_estimator = WinProbabilityEstimator()
    win_estimator.fit(X_train, y_win_train)
    win_probs_test = win_estimator.predict_win_probability(X_test)
    win_auc = roc_auc_score(y_win_test, win_probs_test)
    logger.info(f"Win Probability Estimator ROC-AUC: {round(win_auc, 4)}")

    logger.info("--- Training Economic Rebalancer ---")
    eco_rebalancer = EconomicRebalancer()
    eco_rebalancer.fit(X_train, Y_eco_train)
    pred_eco_test = eco_rebalancer.predict_ratios(X_test)
    eco_mae = mean_absolute_error(Y_eco_test, pred_eco_test)
    logger.info(f"Economic Rebalancer Mean Absolute Error (Ratios): {round(eco_mae, 4)}")

    logger.info("--- Training Stance & Timing Predictor ---")
    stance_predictor = StanceTimingPredictor()
    stance_predictor.fit(X_train, y_stance_train)
    pred_stance_test = [stance_predictor.label_encoder.classes_[i] for i in np.argmax(stance_predictor.predict_proba(X_test), axis=1)]
    stance_acc = accuracy_score(y_stance_test, pred_stance_test)
    logger.info(f"Stance Predictor Test Accuracy: {round(stance_acc * 100, 2)}%")

    # 5. Export to ONNX
    logger.info(f"--- Exporting Models to ONNX in {artifacts_dir} ---")
    exporter = ONNXExporter(num_features=encoder.num_features)
    exported_paths = exporter.export_all(
        strategy_classifier=strategy_clf,
        win_estimator=win_estimator,
        economic_rebalancer=eco_rebalancer,
        stance_predictor=stance_predictor,
        artifacts_dir=artifacts_dir,
    )

    # Also persist scikit-learn models for native fallback
    strategy_clf.save(os.path.join(artifacts_dir, "strategy_classifier.joblib"))
    win_estimator.save(os.path.join(artifacts_dir, "win_probability_estimator.joblib"))
    eco_rebalancer.save(os.path.join(artifacts_dir, "economic_rebalancer.joblib"))
    stance_predictor.save(os.path.join(artifacts_dir, "stance_predictor.joblib"))

    # Also copy to root models/artifacts for project accessibility
    root_artifacts_dir = "models/artifacts"
    if os.path.abspath(root_artifacts_dir) != os.path.abspath(artifacts_dir):
        exporter.export_all(
            strategy_classifier=strategy_clf,
            win_estimator=win_estimator,
            economic_rebalancer=eco_rebalancer,
            stance_predictor=stance_predictor,
            artifacts_dir=root_artifacts_dir,
        )

    logger.info("=== Phase 3 ML Model Development & ONNX Export Complete ===")

    return {
        "strategy_accuracy": round(strat_acc, 4),
        "win_roc_auc": round(win_auc, 4),
        "eco_mae": round(eco_mae, 4),
        "stance_accuracy": round(stance_acc, 4),
        "exported_files": exported_paths,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AoE2 ML Training Pipeline")
    parser.add_argument("--replays-dir", default="data/raw")
    parser.add_argument("--processed-parquet", default="data/processed/snapshots.parquet")
    parser.add_argument("--artifacts-dir", default="aoe2_coach/models/artifacts")
    args = parser.parse_args()

    run_training_pipeline(
        replays_dir=args.replays_dir,
        processed_parquet=args.processed_parquet,
        artifacts_dir=args.artifacts_dir,
    )
