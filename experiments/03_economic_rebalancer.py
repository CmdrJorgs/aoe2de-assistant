# %% [markdown]
# # Experiment — 03_economic_rebalancer: Economic Rebalancer Baseline

# %%
import numpy as np
import skore
from sklearn.model_selection import KFold

from aoe2_coach import PROJECT_ROOT
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.economic_rebalancer import EconomicRebalancer
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset

# %% [markdown]
# ## Open the Project

# %%
project = skore.Project(
    name="aoe2_economic_rebalancer",
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

vills_tot = np.maximum(1, df["player_vills_total"].values)
y_food = (df["player_vills_food"].values / vills_tot).astype(np.float32)

# %% [markdown]
# ## Evaluate Learner

# %%
eco_rebalancer = EconomicRebalancer()
splitter = KFold(n_splits=3, shuffle=True, random_state=42)
report = skore.evaluate(eco_rebalancer.model, X, y_food, splitter=splitter)

# %% [markdown]
# ## Persist Report to Project

# %%
project.put("03_economic_rebalancer", report)

# %%
report
