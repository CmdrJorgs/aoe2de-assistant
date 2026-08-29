# AoE2 Coach AI — Pro Tournament Match Benchmark Report
**Execution Timestamp:** 2026-08-28T20:22:50Z

## 1. Executive Summary & SLA Verification
| Benchmark Metric | Target SLA | Measured Score | Status |
| :--- | :--- | :--- | :--- |
| **Top-1 Strategy Agreement** | $\ge 75.0\%$ | **86.7%** | ✅ PASS |
| **Top-3 Strategy Recall** | $\ge 90.0\%$ | **93.3%** | ✅ PASS |
| **Production Building Match** | $\ge 80.0\%$ | **86.7%** | ✅ PASS |
| **Tactical Stance Agreement** | $\ge 70.0\%$ | **86.7%** | ✅ PASS |
| **Counter Matrix Compliance** | $\ge 90.0\%$ | **100.0%** | ✅ PASS |
| **Macro Rebalance MAE** | $\le 3.5$ vills | **2.31 vills** | ✅ PASS |
| **ML Inference P99 Latency** | $< 20.0$ ms | **1.89 ms** | ✅ PASS |

## 2. Latency Profiling
| Pipeline Stage | Mean | P50 (Median) | P90 | P95 | P99 | Max |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ML ONNX Inference Engine** | 0.45ms | 0.34ms | 0.65ms | 1.28ms | 1.89ms | 2.14ms |
| **Total Recommendation Pipeline** | 0.48ms | 0.37ms | 0.72ms | 1.36ms | 1.95ms | 2.19ms |

## 3. Performance by Game Age
- **Feudal Age Strategy Accuracy:** 100.0%
- **Castle Age Strategy Accuracy:** 90.9%
- **Imperial Age Strategy Accuracy:** 50.0%

## 4. Scenario Breakdown (Top Tournament Matches)
| Scenario ID | Matchup | Age | Recommended Comp | Expected Pro Comp | Stance | ML Latency | Result |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pro-hcv-01-franks-britons` | Hera (Franks) vs TheViper (Britons) | Age 3 | **knight_line** | knight_line, skirm_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-kotd5-02-mayans-huns` | Tatoh (Mayans) vs Liereyy (Huns) | Age 2 | **pike_line** | crossbow_line, skirm_line, pike_line | FORWARD_PRESSURE | 0.4ms | ✅ |
| `pro-warlords2-03-aztecs-franks` | Jordan (Aztecs) vs Yo (Franks) | Age 3 | **pike_line** | monk_line, pike_line, unique_unit_line | DEFENSIVE_TURTLING | 0.2ms | ✅ |
| `pro-rbw-04-byz-goths` | TheViper (Byzantines) vs Daut (Goths) | Age 4 | **unique_unit_line** | unique_unit_line, champion_line | ALL_IN_AGGRESSION | 0.3ms | ✅ |
| `pro-kotd5-05-turks-bohemians` | Capoch (Turks) vs Villese (Bohemians) | Age 3 | **champion_line** | unique_unit_line, siege_line | ALL_IN_AGGRESSION | 0.5ms | ❌ |
| `pro-warlords3-06-mongols-vikings` | Hera (Mongols) vs Tatoh (Vikings) | Age 2 | **scout_line** | scout_line, skirm_line, unique_unit_line | FORWARD_PRESSURE | 0.6ms | ✅ |
| `pro-hcv-07-chinese-franks` | Mr_Yo (Chinese) vs Jordan (Franks) | Age 3 | **pike_line** | camel_line, unique_unit_line, pike_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-rbw-08-ethiopians-britons` | Liereyy (Ethiopians) vs Villese (Britons) | Age 3 | **skirm_line** | crossbow_line, siege_line, skirm_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-kotd4-09-poles-hindustanis` | Daut (Poles) vs Hera (Hindustanis) | Age 3 | **pike_line** | knight_line, pike_line, monk_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-hc4-10-romans-goths` | TheViper (Romans) vs Mr_Yo (Goths) | Age 4 | **knight_line** | champion_line, siege_line, unique_unit_line | ALL_IN_AGGRESSION | 0.3ms | ⚠️ Top-3 |
| `pro-rbw5-11-lith-franks` | Hera (Lithuanians) vs Liereyy (Franks) | Age 3 | **monk_line** | unique_unit_line, knight_line, monk_line | DEFENSIVE_TURTLING | 0.3ms | ✅ |
| `pro-kotd5-12-gurjaras-mayans` | Tatoh (Gurjaras) vs Jordan (Mayans) | Age 3 | **unique_unit_line** | unique_unit_line, camel_line, knight_line | FORWARD_PRESSURE | 0.4ms | ✅ |
| `pro-warlords2-13-khmer-byz` | Capoch (Khmer) vs Daut (Byzantines) | Age 3 | **knight_line** | siege_line, knight_line, unique_unit_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-hcv-14-burgundians-britons` | Yo (Burgundians) vs TheViper (Britons) | Age 3 | **knight_line** | knight_line, skirm_line | FORWARD_PRESSURE | 0.3ms | ✅ |
| `pro-kotd5-15-saracens-franks` | Liereyy (Saracens) vs Hera (Franks) | Age 3 | **camel_line** | camel_line, unique_unit_line, monk_line | ALL_IN_AGGRESSION | 0.4ms | ✅ |