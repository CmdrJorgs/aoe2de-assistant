import numpy as np
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator


def test_smoke_win_probability_matchup_features():
    df = generate_augmented_training_dataset(num_synthetic_samples=50)
    encoder = FeatureEncoder()
    X = encoder.encode_dataframe(df)
    assert X.shape[1] == encoder.num_features
    assert "cav_matchup_delta" in encoder.feature_names
    assert "eco_kill_rate_est" in encoder.feature_names
    y = df["label_winner"].astype(int).values
    win_estimator = WinProbabilityEstimator()
    win_estimator.model.fit(X, y)
    preds = win_estimator.model.predict_proba(X[:5])
    assert preds.shape == (5, 2)
