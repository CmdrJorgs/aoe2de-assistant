# %% [markdown]
# # Experiment — 04_stance_timing: Stance Timing Predictor Baseline

# %%
import numpy as np
import skore
from sklearn.model_selection import KFold

from aoe2_coach import PROJECT_ROOT
from aoe2_coach.models.feature_encoder import FeatureEncoder
from aoe2_coach.models.stance_timing_predictor import StanceTimingPredictor, STANCE_CLASSES
from aoe2_coach.models.train_pipeline import generate_augmented_training_dataset

# %% [markdown]
# ## Open the Project

# %%
project = skore.Project(
    name="aoe2_stance_timing",
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

stance_predictor = StanceTimingPredictor()
y = np.array([
    stance_predictor.label_encoder.transform([s if s in STANCE_CLASSES else "FORWARD_PRESSURE"])[0]
    for s in df["label_stance"].fillna("FORWARD_PRESSURE")
])

# %% [markdown]
# ## Evaluate Learner

# %%
splitter = KFold(n_splits=3, shuffle=True, random_state=42)
report = skore.evaluate(stance_predictor.model, X, y, splitter=splitter)

# %% [markdown]
# ## Persist Report to Project

# %%
project.put("04_stance_timing", report)

# %%
report
