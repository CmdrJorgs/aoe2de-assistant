# %% [markdown]
# # Audit — 01_strategy_classifier: Strategy Classifier Baseline
#
# Read-only review of the stored report below: its checks and metrics.

# %%
import skore

from aoe2_coach import PROJECT_ROOT

# %% [markdown]
# ## Open the project
#
# Open the same project the experiment wrote to.

# %%
project = skore.Project(
    name="aoe2_strategy_classifier",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project

# %% [markdown]
# ## List the available reports

# %%
summary = project.summarize()
summary

# %% [markdown]
# ## Load the report

# %%
df_summary = summary.frame()
REPORT_ID = df_summary.loc[df_summary["name"] == "01_strategy_classifier", "report_id"].iloc[0]

report = project.get(REPORT_ID)
report

# %% [markdown]
# ## Checks summary

# %%
report.checks.summarize().frame()

# %% [markdown]
# ## Metrics summary

# %%
report.metrics.summarize().frame()

# %% [markdown]
# ## End of audit
