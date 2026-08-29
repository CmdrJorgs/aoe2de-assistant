# %% [markdown]
# # Experiment — 05_win_probability_matchup_features: Win Probability with Civ Interactions & Eco Kills

# %%
import numpy as np
import skore
from sklearn.model_selection import KFold

from aoe2_coach import PROJECT_ROOT
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.win_probability_estimator import WinProbabilityEstimator
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset

# %% [markdown]
# ## Open the Project

# %%
project = skore.Project(
    name="aoe2_win_probability",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## Load and Prepare Data with Enhanced Features

# %%
df = generate_augmented_training_dataset(num_synthetic_samples=1000)
encoder = FeatureEncoder()
X = encoder.encode_dataframe(df)
y = df["label_winner"].astype(int).values

# %% [markdown]
# ## Evaluate Learner

# %%
win_estimator = WinProbabilityEstimator()
splitter = KFold(n_splits=3, shuffle=True, random_state=42)
report = skore.evaluate(win_estimator.model, X, y, splitter=splitter)

# %% [markdown]
# ## Persist Report to Project

# %%
project.put("05_win_probability_matchup_features", report)

# %%
report
