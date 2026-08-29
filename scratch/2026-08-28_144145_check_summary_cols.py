import skore
from aoe2_coach import PROJECT_ROOT

p = skore.Project(name="aoe2_strategy_classifier", mode="local", workspace=str(PROJECT_ROOT / "reports"))
s = p.summarize()
df = s.frame()
print("report_id:", df["report_id"].iloc[0])
print("name:", df["name"].iloc[0])
print("key:", df["key"].iloc[0])
rep_by_id = p.get(df["report_id"].iloc[0])
print("Got by report_id:", rep_by_id)
rep_by_key = p.get("01_strategy_classifier")
print("Got by key directly:", rep_by_key)
