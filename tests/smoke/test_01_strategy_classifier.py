import numpy as np
from sklearn.model_selection import KFold
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.strategy_classifier import StrategyClassifier, map_label_to_canonical_comp


def test_smoke_strategy_classifier():
    df = generate_augmented_training_dataset(num_synthetic_samples=50)
    encoder = FeatureEncoder()
    X = encoder.encode_dataframe(df)
    strat_clf = StrategyClassifier()
    y = np.array([
        strat_clf.label_encoder.transform([map_label_to_canonical_comp(lbl)])[0]
        for lbl in df["label_primary_comp"].fillna("knight_line")
    ])
    strat_clf.comp_model.fit(X, y)
    preds = strat_clf.comp_model.predict(X[:5])
    assert len(preds) == 5
