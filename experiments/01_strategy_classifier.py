# %% [markdown]
# # Experiment — 01_strategy_classifier: Strategy Classifier Baseline

# %%
import numpy as np
import skore
from sklearn.model_selection import KFold

from aoe2_coach import PROJECT_ROOT
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.strategy_classifier import StrategyClassifier, map_label_to_canonical_comp
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset

# %% [markdown]
# ## Open the Project

# %%
project = skore.Project(
    name="aoe2_strategy_classifier",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## Load and Prepare Data

# %%
df = generate_augmented_training_dataset(num_synthetic_samples=1000)
encoder = FeatureEncoder()
X = encoder.encode_dataframe(df)

strat_clf = StrategyClassifier()
y = np.array([
    strat_clf.label_encoder.transform([map_label_to_canonical_comp(lbl)])[0]
    for lbl in df["label_primary_comp"].fillna("knight_line")
])

# %% [markdown]
# ## Evaluate Learner

# %%
splitter = KFold(n_splits=3, shuffle=True, random_state=42)
report = skore.evaluate(strat_clf.comp_model, X, y, splitter=splitter)

# %% [markdown]
# ## Persist Report to Project

# %%
project.put("01_strategy_classifier", report)

# %%
report
