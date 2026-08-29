import skore
from aoe2_coach import PROJECT_ROOT

projects = [
    ("01_strategy_classifier", "aoe2_strategy_classifier"),
    ("02_win_probability", "aoe2_win_probability"),
    ("03_economic_rebalancer", "aoe2_economic_rebalancer"),
    ("04_stance_timing", "aoe2_stance_timing"),
]

for stem, proj_name in projects:
    p = skore.Project(name=proj_name, mode="local", workspace=str(PROJECT_ROOT / "reports"))
    s = p.summarize()
    print(f"\n--- Project: {proj_name} ---")
    print(s)
