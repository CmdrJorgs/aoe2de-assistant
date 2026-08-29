# Cells: `audit/01_strategy_classifier.py`

## Cell 0: `# %% [markdown]`

# Audit — 01_strategy_classifier: Strategy Classifier Baseline
#
Read-only review of the stored report below: its checks and metrics.

## Cell 1: `# %%`

```python
import skore

from aoe2_coach import PROJECT_ROOT
```

## Cell 2: `# %% [markdown]`

## Open the project
#
Open the same project the experiment wrote to.

## Cell 3: `# %%`

```python
project = skore.Project(
    name="aoe2_strategy_classifier",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project
```

**stdout:**
```
Out[0]: Project(name='aoe2_strategy_classifier', mode='local', workspace='/home/djorgs/Documents/git/aoe2-coach/reports')
```

## Cell 4: `# %% [markdown]`

## List the available reports

## Cell 5: `# %%`

```python
summary = project.summarize()
summary
```

**stdout:**
```
Out[0]: 
                                       skore-version  \
  id                                                   
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb        0.25.0   

                                                           creation-date  \
  id                                                                       
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  2026-08-28T20:41:04.701210+00:00   

                                             report_type  \
  id                                                       
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  cross-validation   

                                                                                           git_commit  \
  id                                                                                                    
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  c634cf0c2227ad20d5fe3c096678d78d69378355 (working tree dirty)   

                                                                   report_id  \
  id                                                                           
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  01a04a1a-c9bc-7c97-bb14-b815e684c5fb   

                                                          ml_task  \
  id                                                                
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  multiclass-classification   

                                                                                                                                              learner  \
  id                                                                                                                                                    
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  RandomForestClassifier(max_depth=12, min_samples_split=4, n_jobs=-1,\n                       random_state=42)   

                                                          name  \
  id                                                             
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  01_strategy_classifier   

                                                                                                                                                                                                                                         local_path  \
  id                                                                                                                                                                                                                                                  
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  /home/djorgs/Documents/git/aoe2-coach/reports/projects/aoe2_strategy_classifier/reports/2026-08-28T20-41-04.701210+00-00__id_01a04a1a-c9bc-7c97-bb14-b815e684c5fb__cross-validation__01_strategy_classifier   

                                                                   date  \
  id                                                                      
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb 2026-08-28 20:41:04.701210+00:00   

                                                           key  \
  id                                                             
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  01_strategy_classifier   

                                                                 dataset  \
  id                                                                       
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  cc40facccecb6b5dc1dcaddb1e33e4bf   

                                        accuracy  fit_time  log_loss  \
  id                                                                   
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb  0.996997  0.082902  0.079548   

                                        precision  precision_avg  \
  id                                                               
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb   0.998613       0.998613   

                                        predict_time    recall  recall_avg  \
  id                                                                         
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb      0.013628  0.992481    0.992481   

                                        roc_auc  roc_auc_avg  
  id                                                          
0 01a04a1a-c9bc-7c97-bb14-b815e684c5fb      1.0          1.0  
```

## Cell 6: `# %% [markdown]`

## Load the report

## Cell 7: `# %%`

```python
df_summary = summary.frame()
REPORT_ID = df_summary.loc[df_summary["name"] == "01_strategy_classifier", "report_id"].iloc[0]

report = project.get(REPORT_ID)
report
```

**stdout:**
```
Out[0]: 










CrossValidationReport:
        'RandomForestClassifier'

                                            mean           std
Metric           Label Average                        
Accuracy                        0.996997  5.201354e-03
Precision        0              1.000000  0.000000e+00
                 1              1.000000  0.000000e+00
                 2              0.990291  1.681603e-02
                 3              1.000000  0.000000e+00
                 5              1.000000  0.000000e+00
                 6              1.000000  0.000000e+00
                 8              1.000000  0.000000e+00
                       macro    0.998613  2.402290e-03
Recall           0              0.964912  6.077371e-02
                 1              1.000000  0.000000e+00
                 2              1.000000  0.000000e+00
                 3              1.000000  0.000000e+00
                 5              0.982456  3.038686e-02
                 6              1.000000  0.000000e+00
                 8              1.000000  0.000000e+00
                       macro    0.992481  1.302294e-02
ROC AUC          0              1.000000  0.000000e+00
                 1              1.000000  1.570092e-16
                 2              1.000000  0.000000e+00
                 3              1.000000  0.000000e+00
                 5              1.000000  0.000000e+00
                 6              1.000000  7.850462e-17
                 8              1.000000  1.570092e-16
                       macro    1.000000  0.000000e+00
Log loss                        0.079548  4.820075e-03
Fit time (s)                    0.082902  2.569437e-03
Predict time (s)                0.013628  1.088523e-04
        Call `report.to_markdown()` for a markdown summary of the report's contents.
```

**stderr:**
```
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_checks/model_checks.py:489: ConstantInputWarning: An input array is constant; the correlation coefficient is not defined.
  corr_statistic = spearmanr(X.to_numpy()).statistic
```

## Cell 8: `# %% [markdown]`

## Checks summary

## Cell 9: `# %%`

```python
report.checks.summarize().frame()
```

**stdout:**
```










































































































































Out[0]: 
      code                                                title  \
0   SKD001                                Potential overfitting   
1   SKD002                               Potential underfitting   
2   SKD003               Inconsistent performance across splits   
3   SKD004                                 High class imbalance   
4   SKD005                             Underrepresented classes   
5   SKD006                           Coefficient interpretation   
6   SKD007             MDI biased for high-cardinality features   
7   SKD008                     Highly correlated input features   
8   SKD009  Model performance vs. HistGradientBoosting baseline   
9   SKD010                           Model slower than baseline   
10  SKD011                                       Golden feature   
11  SKD012                                     Useless features   
12  SKD013                    Train-test overlap in time series   
13  SKD014                       Hyperparameters at search edge   
14  SKD015                         Hyperparameters worth tuning   
15  SKD016                                  Estimator not tuned   

           section  \
0           passed   
1           passed   
2           passed   
3   not_applicable   
4            issue   
5   not_applicable   
6              tip   
7            issue   
8              tip   
9           passed   
10             tip   
11             tip   
12  not_applicable   
13  not_applicable   
14  not_applicable   
15          passed   

                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         explanation  \
0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                NaN   
1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                NaN   
2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                NaN   
3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               ML task is not binary classification. Got multiclass-classification.   
4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          Classes [6, 0, 5, 8] each represent less than 10% of the dataset samples. Accuracy should not be used alone to assess model performance as it may be misleading by ignoring poor performance on underrepresented classes.   
5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Estimator is not a linear model: it does not have a `coef_` attribute.   
6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                  High-cardinality features detected: Feature 0, Feature 4, Feature 5 (and 6 more). Mean Decrease in Impurity (MDI) importance is biased toward such features. Consider using permutation importance for a more robust alternative.   
7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            5 pair(s) of features have a Spearman correlation above 0.9. Highly correlated features can destabilize linear model coefficients and feature-importance estimates, and may cause collinearity-induced numerical issues.Dropping redundant features may also improve model performance.   
8                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          Your model is on par with or better than a HistGradientBoosting baseline. Baseline performance on the test set, for reference: Accuracy=1, Log loss=0.000411, Precision (0)=1, Precision (1)=1, Precision (2)=1, Precision (3)=1, Precision (5)=1, Precision (6)=1, Precision (8)=1, Precision (macro)=1, ROC AUC (0)=1, ROC AUC (1)=1, ROC AUC (2)=1, ROC AUC (3)=1, ROC AUC (5)=1, ROC AUC (6)=1, ROC AUC (8)=1, ROC AUC (macro)=1, Recall (0)=1, Recall (1)=1, Recall (2)=1, Recall (3)=1, Recall (5)=1, Recall (6)=1, Recall (8)=1, Recall (macro)=1.   
9                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                NaN   
10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         A model trained on feature(s) ['Feature 22', 'Feature 23', 'Feature 24'] alone has similar performance to a model trained on all the features, on the default predictive metrics. This may signal data leakage or excessive reliance on a single feature.   
11  Feature(s) ['Feature #0', 'Feature #1', 'Feature #10', 'Feature #11', 'Feature #12', 'Feature #13', 'Feature #14', 'Feature #15', 'Feature #16', 'Feature #17', 'Feature #18', 'Feature #19', 'Feature #2', 'Feature #20', 'Feature #21', 'Feature #22', 'Feature #25', 'Feature #26', 'Feature #27', 'Feature #28', 'Feature #29', 'Feature #3', 'Feature #30', 'Feature #31', 'Feature #32', 'Feature #33', 'Feature #34', 'Feature #36', 'Feature #37', 'Feature #38', 'Feature #39', 'Feature #4', 'Feature #40', 'Feature #41', 'Feature #42', 'Feature #43', 'Feature #44', 'Feature #45', 'Feature #46', 'Feature #47', 'Feature #48', 'Feature #49', 'Feature #5', 'Feature #50', 'Feature #51', 'Feature #52', 'Feature #53', 'Feature #54', 'Feature #55', 'Feature #56', 'Feature #57', 'Feature #58', 'Feature #59', 'Feature #6', 'Feature #60', 'Feature #61', 'Feature #62', 'Feature #63', 'Feature #64', 'Feature #7', 'Feature #8', 'Feature #9'] have permutation importance overlapping with zero and could likely be dropped without degrading performance. Dropping redundant features may also improve model performance.   
12                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   Input data is not a narwhals compatible DataFrame. Got ndarray.   
13                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Estimator is not a BaseSearchCV instance. Got RandomForestClassifier.   
14                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             Estimator is not a BaseSearchCV instance. Got RandomForestClassifier.   
15                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                               NaN   

                                                                                          documentation_url  
0                    https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd001-overfitting  
1                   https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd002-underfitting  
2       https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd003-inconsistent-performance  
3           https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd004-high-class-imbalance  
4       https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd005-underrepresented-classes  
5          https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd006-unscaled-coefficients  
6           https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd007-mdi-cardinality-bias  
7            https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd008-correlated-features  
8            https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd009-worse-than-baseline  
9           https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd010-slower-than-baseline  
10                https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd011-golden-feature  
11              https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd012-useless-features  
12       https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd013-train-test-time-overlap  
13    https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd014-hyperparams-at-search-edge  
14  https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd015-hyperparameters-worth-tuning  
15           https://docs.skore.probabl.ai/0.25/user_guide/automated_checks.html#skd016-estimator-not-tuned  
```

## Cell 10: `# %% [markdown]`

## Metrics summary

## Cell 11: `# %%`

```python
report.metrics.summarize().frame()
```

**stdout:**
```

Out[0]: 
                     randomforestclassifier_mean  randomforestclassifier_std
accuracy                                0.996997                5.201354e-03
precision_0                             1.000000                0.000000e+00
precision_1                             1.000000                0.000000e+00
precision_2                             0.990291                1.681603e-02
precision_3                             1.000000                0.000000e+00
precision_5                             1.000000                0.000000e+00
precision_6                             1.000000                0.000000e+00
precision_8                             1.000000                0.000000e+00
precision_avg_macro                     0.998613                2.402290e-03
recall_0                                0.964912                6.077371e-02
recall_1                                1.000000                0.000000e+00
recall_2                                1.000000                0.000000e+00
recall_3                                1.000000                0.000000e+00
recall_5                                0.982456                3.038686e-02
recall_6                                1.000000                0.000000e+00
recall_8                                1.000000                0.000000e+00
recall_avg_macro                        0.992481                1.302294e-02
roc_auc_0                               1.000000                0.000000e+00
roc_auc_1                               1.000000                1.570092e-16
roc_auc_2                               1.000000                0.000000e+00
roc_auc_3                               1.000000                0.000000e+00
roc_auc_5                               1.000000                0.000000e+00
roc_auc_6                               1.000000                7.850462e-17
roc_auc_8                               1.000000                1.570092e-16
roc_auc_avg_macro                       1.000000                0.000000e+00
log_loss                                0.079548                4.820075e-03
fit_time                                0.082902                2.569437e-03
predict_time                            0.013628                1.088523e-04
```

## Cell 12: `# %% [markdown]`

## End of audit
