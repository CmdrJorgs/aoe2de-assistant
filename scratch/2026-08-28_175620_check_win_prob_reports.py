import skore
from aoe2_coach import PROJECT_ROOT

p = skore.Project(name="aoe2_win_probability", mode="local", workspace=str(PROJECT_ROOT / "reports"))
s = p.summarize()
df = s.frame()
print(df[["name", "report_id", "accuracy", "roc_auc", "log_loss"]])
