"""
Try to reproduce evoked response results from Wynn et al (2019)

Check if erps are significantly different for parietal sensors in (0.4, 0.8)
time window.

For analysis compute evoked responses by averaging within each subject and
condition and fit random intercept mixed effects linear model with subject
being a random effect and condition being a fixed one

RESULTS
-------
ERP difference appears to be non-significant.

Magnetometers
          Mixed Linear Model Regression Results
==========================================================
Model:             MixedLM  Dependent Variable:  data
No. Observations:  84       Method:              REML
No. Groups:        28       Scale:               0.9453
Min. group size:   3        Log-Likelihood:      -143.0042
Max. group size:   3        Converged:           Yes
Mean group size:   3.0
----------------------------------------------------------
                Coef.  Std.Err.   z    P>|z| [0.025 0.975]
----------------------------------------------------------
Intercept        0.466    0.310  1.502 0.133 -0.142  1.073
cond[T.LOW HIT] -0.427    0.260 -1.644 0.100 -0.936  0.082
cond[T.MISS]    -0.314    0.260 -1.209 0.227 -0.823  0.195
subj Var         1.746    0.706
==========================================================

Gradiometers
          Mixed Linear Model Regression Results
==========================================================
Model:               MixedLM  Dependent Variable:  data
No. Observations:    84       Method:              REML
No. Groups:          28       Scale:               0.0116
Min. group size:     3        Log-Likelihood:      40.8474
Max. group size:     3        Converged:           Yes
Mean group size:     3.0
----------------------------------------------------------
                Coef.  Std.Err.   z    P>|z| [0.025 0.975]
----------------------------------------------------------
Intercept       -0.037    0.029 -1.256 0.209 -0.095  0.021
cond[T.LOW HIT]  0.049    0.029  1.703 0.089 -0.007  0.106
cond[T.MISS]     0.029    0.029  1.000 0.317 -0.028  0.085
subj Var         0.013    0.051
==========================================================
"""
import statsmodels.formula.api as smf
from statsmodels.stats.diagnostic import het_white
import matplotlib.pyplot as plt
import numpy as np

from metacog.dataset_specific_utils import assemble_epochs_new
from metacog.group_analysis.reproduce_wynn.utils import prepare_erp
import scipy.stats as st
import seaborn as sns
import matplotlib

time_window = (0.4, 0.8)
ch_group = "parietal"
ch_type = "grad"

X, meta, times, info = assemble_epochs_new(ch_type=ch_type, baseline=None)
df, data = prepare_erp(times, time_window, ch_group, meta, X, info)
if ch_type == "mag":
    df.data *= 1e14
elif ch_type == "grad":
    df.data *= 1e12


md = smf.mixedlm("data ~ cond", data=df, groups="subj")
mdf = md.fit()
print(mdf.summary())


legend = []
times_sel = times[
    np.logical_and(times >= time_window[0], times < time_window[1])
]
for cond in np.unique(df.cond):
    plt.plot(times, data[df.cond == cond, :, :].mean(axis=(0, 1)))
    legend.append(cond)
plt.legend(legend)
plt.show()

font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 22}
matplotlib.rc('font', **font)
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
