import numpy as np
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES


def test_smoke_stance_timing():
    df = generate_augmented_training_dataset(num_synthetic_samples=50)
    encoder = FeatureEncoder()
    X = encoder.encode_dataframe(df)
    stance_predictor = StanceTimingPredictor()
    y = np.array([
        stance_predictor.label_encoder.transform([s if s in STANCE_CLASSES else "FORWARD_PRESSURE"])[0]
        for s in df["label_stance"].fillna("FORWARD_PRESSURE")
    ])
    stance_predictor.model.fit(X, y)
    preds = stance_predictor.model.predict(X[:5])
    assert len(preds) == 5
