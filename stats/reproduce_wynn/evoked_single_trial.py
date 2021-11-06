"""
Try to reproduce evoked response results from Wynn et al (2019)
Single-trial analysis, following ./evoked.py

Check if erps are significantly different for parietal sensors in (0.4, 0.8)
time window.

For analysis compute evoked responses by averaging within each subject and
condition and fit random intercept mixed effects linear model with subject
being a random effect and condition being a fixed one

RESULTS
-------

             Mixed Linear Model Regression Results
===============================================================
Model:                MixedLM   Dependent Variable:   data
No. Observations:     1645      Method:               REML
No. Groups:           28        Scale:                0.1750
Min. group size:      36        Log-Likelihood:       -932.2522
Max. group size:      80        Converged:            Yes
Mean group size:      58.8
---------------------------------------------------------------
                     Coef.  Std.Err.   z    P>|z| [0.025 0.975]
---------------------------------------------------------------
Intercept            -0.042    0.030 -1.399 0.162 -0.101  0.017
condition[T.LOW HIT]  0.064    0.032  1.996 0.046  0.001  0.128
condition[T.MISS]     0.031    0.024  1.287 0.198 -0.016  0.078
subject Var           0.015    0.012
===============================================================
"""
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import numpy as np

from metacog.dataset_specific_utils import assemble_epochs_new
from metacog.group_analysis.reproduce_wynn.utils import (
    _drop_by_confidence,
    add_condition,
    _get_masks,
)
from statsmodels.stats.diagnostic import het_white
import scipy.stats as st
import seaborn as sns

time_window = (0.4, 0.8)
ch_group = "parietal"
ch_type = "grad"

X, meta, times, info = assemble_epochs_new(ch_type=ch_type, baseline=None)
df, data = _drop_by_confidence(meta, X, 0, 30, 70, 100)
df = add_condition(df, 30, 70)
time_inds, ch_inds = _get_masks(
    times, time_window[0], time_window[1], ch_group, info
)
data = (
    data[:, np.squeeze(ch_inds), :]
    .mean(axis=1)[:, np.squeeze(time_inds)]
    .mean(axis=1)
)
df["data"] = data
if ch_type == "mag":
    df.data *= 1e14
elif ch_type == "grad":
    df.data *= 1e12


md = smf.mixedlm("data ~ condition", data=df, groups="subject")
mdf = md.fit()
print(mdf.summary())

# legend = []
# times_sel = times[
#     np.logical_and(times >= time_window[0], times < time_window[1])
# ]
# for cond in np.unique(df.condition):
#     plt.plot(times, data[df.condition == cond, :, :].mean(axis=(0, 1)))
#     legend.append(cond)
# plt.legend(legend)
# plt.show()

# QQ-plot shows that our data are not normal. Something to think about
fig = plt.figure(figsize=(16, 9))
ax = fig.add_subplot(111)
# st.probplot(df.target, plot=ax)
st.probplot(mdf.resid, plot=ax)
plt.show()

fig = plt.figure(figsize=(16, 9))
ax = sns.distplot(
    mdf.resid, hist=False, kde_kws={"shade": True, "lw": 1}, fit=st.norm
)
ax.set_xlabel("Residuals")
plt.show()

labels = ["Statistic", "p-value"]
norm_res = st.shapiro(mdf.resid)
for key, val in dict(zip(labels, norm_res)).items():
    print(key, val)

fig = plt.figure(figsize=(16, 9))
ax = sns.scatterplot(y=mdf.resid, x=mdf.fittedvalues)
ax.set_xlabel("Fitted Values")
ax.set_ylabel("Residuals")
plt.show()

het_white_res = het_white(mdf.resid, mdf.model.exog)
labels = ["LM Statistic", "LM-Test p-value", "F-Statistic", "F-Test p-value"]
for key, val in dict(zip(labels, het_white_res)).items():
    print(key, val)

fig = plt.figure(figsize=(16, 9))
ax = sns.boxplot(x=mdf.model.groups, y=mdf.resid)
ax.set_ylabel("Residuals")
ax.set_xlabel("Subjects")
plt.show()
