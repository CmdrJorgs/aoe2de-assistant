# Cells: `audit/04_stance_timing.py`

## Cell 0: `# %% [markdown]`

# Audit — 04_stance_timing: Stance Timing Predictor Baseline
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
    name="aoe2_stance_timing",
    mode="local",
    workspace=str(PROJECT_ROOT / "reports"),
)
project
```

**stdout:**
```
Out[0]: Project(name='aoe2_stance_timing', mode='local', workspace='/home/djorgs/Documents/git/aoe2-coach/reports')
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
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5        0.25.0   

                                                           creation-date  \
  id                                                                       
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  2026-08-28T20:41:10.422447+00:00   

                                             report_type  \
  id                                                       
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  cross-validation   

                                                                                           git_commit  \
  id                                                                                                    
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  c634cf0c2227ad20d5fe3c096678d78d69378355 (working tree dirty)   

                                                                   report_id  \
  id                                                                           
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  01a04a1a-e016-70a1-8d10-3bcb14a678b5   

                                                          ml_task  \
  id                                                                
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  multiclass-classification   

                                                                                                                                              learner  \
  id                                                                                                                                                    
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  RandomForestClassifier(max_depth=10, min_samples_split=4, n_jobs=-1,\n                       random_state=42)   

                                                    name  \
  id                                                       
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  04_stance_timing   

                                                                                                                                                                                                                             local_path  \
  id                                                                                                                                                                                                                                      
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  /home/djorgs/Documents/git/aoe2-coach/reports/projects/aoe2_stance_timing/reports/2026-08-28T20-41-10.422447+00-00__id_01a04a1a-e016-70a1-8d10-3bcb14a678b5__cross-validation__04_stance_timing   

                                                                   date  \
  id                                                                      
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5 2026-08-28 20:41:10.422447+00:00   

                                                     key  \
  id                                                       
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  04_stance_timing   

                                                                 dataset  \
  id                                                                       
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  ac730ded79bafd201ac3c62d8692ee29   

                                        accuracy  fit_time  log_loss  \
  id                                                                   
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5  0.946009  0.086488       NaN   

                                        precision  precision_avg  \
  id                                                               
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5   0.596907       0.613052   

                                        predict_time    recall  recall_avg  \
  id                                                                         
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5      0.013836  0.529734     0.51916   

                                        roc_auc  roc_auc_avg  
  id                                                          
0 01a04a1a-e016-70a1-8d10-3bcb14a678b5      NaN          NaN  
```

## Cell 6: `# %% [markdown]`

## Load the report

## Cell 7: `# %%`

```python
df_summary = summary.frame()
REPORT_ID = df_summary.loc[df_summary["name"] == "04_stance_timing", "report_id"].iloc[0]

report = project.get(REPORT_ID)
report
```

**stdout:**
```
Out[0]: 










CrossValidationReport:
        'RandomForestClassifier'

                                            mean       std
Metric           Label Average                    
Accuracy                        0.946009  0.008915
Precision        0              0.968750  0.009439
                 1              0.000000  0.000000
                 2              0.923771  0.040460
                 3              0.500000  0.500000
                       macro    0.613052  0.097073
Recall           0              0.998308  0.002931
                 1              0.000000  0.000000
                 2              0.938827  0.008562
                 3              0.172161  0.151606
                       macro    0.519160  0.051633
ROC AUC                              NaN       NaN
Log loss                             NaN       NaN
Fit time (s)                    0.086488  0.003227
Predict time (s)                0.013836  0.000588
Precision        4              0.909091       NaN
Recall           4              0.967742       NaN
        Call `report.to_markdown()` for a markdown summary of the report's contents.
```

**stderr:**
```
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_cross_validation/report.py:603: UserWarning: Metric 'roc_auc' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'roc_auc_avg' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 4 vs 5. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 3 4]')
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 5 vs 4. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 2 3 4]')
  .frame(verbose_name=True, flat_index=False)
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_cross_validation/report.py:667: UserWarning: Metric 'roc_auc' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'roc_auc_avg' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 4 vs 5. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 3 4]')
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 5 vs 4. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 2 3 4]')
  .frame(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_checks/model_checks.py:266: UserWarning: Metric 'roc_auc' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'roc_auc_avg' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 4 vs 5. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 3 4]')
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 5 vs 4. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 2 3 4]')
  report_data = report.metrics.summarize(data_source="test").frame(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_checks/model_checks.py:489: ConstantInputWarning: An input array is constant; the correlation coefficient is not defined.
  corr_statistic = spearmanr(X.to_numpy()).statistic
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/skore/_sklearn/_estimator/report.py:776: UserWarning: Metric 'roc_auc' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'roc_auc_avg' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 4 vs 5. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 3 4]')
  metrics_frame = self.metrics.summarize(data_source="test").frame(
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
0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 NaN   
1                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 NaN   
2                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 NaN   
3                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                ML task is not binary classification. Got multiclass-classification.   
4                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              Classes [4, 1, 2] each represent less than 10% of the dataset samples. Accuracy should not be used alone to assess model performance as it may be misleading by ignoring poor performance on underrepresented classes.   
5                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              Estimator is not a linear model: it does not have a `coef_` attribute.   
6                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   High-cardinality features detected: Feature 0, Feature 4, Feature 5 (and 6 more). Mean Decrease in Impurity (MDI) importance is biased toward such features. Consider using permutation importance for a more robust alternative.   
7                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             5 pair(s) of features have a Spearman correlation above 0.9. Highly correlated features can destabilize linear model coefficients and feature-importance estimates, and may cause collinearity-induced numerical issues.Dropping redundant features may also improve model performance.   
8                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           Your model is on par with or better than a HistGradientBoosting baseline. Baseline performance on the test set, for reference: Accuracy=0.982, Log loss=nan, Precision (0)=0.993, Precision (1)=0.267, Precision (2)=0.592, Precision (3)=0.869, Precision (4)=0.938, Precision (macro)=0.702, ROC AUC=nan, Recall (0)=0.995, Recall (1)=0.4, Recall (2)=0.592, Recall (3)=0.912, Recall (4)=0.929, Recall (macro)=0.739.   
9                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 NaN   
10                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                      A model trained on feature(s) ['Feature 60'] alone has similar performance to a model trained on all the features, on the default predictive metrics. This may signal data leakage or excessive reliance on a single feature.   
11  Feature(s) ['Feature #0', 'Feature #1', 'Feature #10', 'Feature #11', 'Feature #12', 'Feature #13', 'Feature #14', 'Feature #15', 'Feature #16', 'Feature #17', 'Feature #18', 'Feature #19', 'Feature #2', 'Feature #20', 'Feature #21', 'Feature #22', 'Feature #23', 'Feature #24', 'Feature #25', 'Feature #27', 'Feature #28', 'Feature #29', 'Feature #3', 'Feature #30', 'Feature #31', 'Feature #32', 'Feature #33', 'Feature #35', 'Feature #37', 'Feature #38', 'Feature #39', 'Feature #4', 'Feature #40', 'Feature #41', 'Feature #42', 'Feature #43', 'Feature #44', 'Feature #45', 'Feature #46', 'Feature #47', 'Feature #48', 'Feature #49', 'Feature #5', 'Feature #50', 'Feature #51', 'Feature #52', 'Feature #53', 'Feature #54', 'Feature #55', 'Feature #56', 'Feature #57', 'Feature #58', 'Feature #59', 'Feature #6', 'Feature #61', 'Feature #62', 'Feature #63', 'Feature #64', 'Feature #7', 'Feature #8', 'Feature #9'] have permutation importance overlapping with zero and could likely be dropped without degrading performance. Dropping redundant features may also improve model performance.   
12                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    Input data is not a narwhals compatible DataFrame. Got ndarray.   
13                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              Estimator is not a BaseSearchCV instance. Got RandomForestClassifier.   
14                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              Estimator is not a BaseSearchCV instance. Got RandomForestClassifier.   
15                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                NaN   

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

**stderr:**
```
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
/home/djorgs/Documents/git/aoe2-coach/.venv/lib/python3.12/site-packages/sklearn/model_selection/_split.py:812: UserWarning: The least populated class in y has only 2 members, which is less than n_splits=5.
  warnings.warn(
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
accuracy                                0.946009                    0.008915
precision_0                             0.968750                    0.009439
precision_1                             0.000000                    0.000000
precision_2                             0.923771                    0.040460
precision_3                             0.500000                    0.500000
precision_avg_macro                     0.613052                    0.097073
recall_0                                0.998308                    0.002931
recall_1                                0.000000                    0.000000
recall_2                                0.938827                    0.008562
recall_3                                0.172161                    0.151606
recall_avg_macro                        0.519160                    0.051633
roc_auc                                      NaN                         NaN
roc_auc_avg                                  NaN                         NaN
log_loss                                     NaN                         NaN
fit_time                                0.086488                    0.003227
predict_time                            0.013836                    0.000588
precision_4                             0.909091                         NaN
recall_4                                0.967742                         NaN
```

**stderr:**
```
<ipython-input-1-93faf9ded117>:1: UserWarning: Metric 'roc_auc' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'roc_auc_avg' has failed: ValueError("Number of classes in y_true not equal to the number of columns in 'y_score'")
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 4 vs 5. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 3 4]')
Metric 'log_loss' has failed: ValueError('y_true and y_prob contain different number of classes: 5 vs 4. Please provide the true labels explicitly through the labels argument. Classes found in y_true: [0 1 2 3 4]')
  report.metrics.summarize().frame()
```

## Cell 12: `# %% [markdown]`

## End of audit
