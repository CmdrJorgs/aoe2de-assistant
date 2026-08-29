import numpy as np
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer


def test_smoke_economic_rebalancer():
    df = generate_augmented_training_dataset(num_synthetic_samples=50)
    encoder = FeatureEncoder()
    X = encoder.encode_dataframe(df)
    vills_tot = np.maximum(1, df["player_vills_total"].values)
    y_food = (df["player_vills_food"].values / vills_tot).astype(np.float32)
    eco_rebalancer = EconomicRebalancer()
    eco_rebalancer.model.fit(X, y_food)
    preds = eco_rebalancer.model.predict(X[:5])
    assert len(preds) == 5
