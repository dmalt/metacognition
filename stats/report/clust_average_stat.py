"""
Mixed model for average ERP within a cluster of difference with no repeated
measures correction shows marginally significant effect

DORSO-PARIETAL CLUSTER

GRADIOMETERS

                 Mixed Linear Model Regression Results
========================================================================
Model:                  MixedLM      Dependent Variable:      target
No. Observations:       2708         Method:                  REML
No. Groups:             28           Scale:                   11.7067
Min. group size:        60           Log-Likelihood:          -7235.4650
Max. group size:        112          Converged:               Yes
Mean group size:        96.7
------------------------------------------------------------------------
                              Coef.  Std.Err.   z    P>|z| [0.025 0.975]
------------------------------------------------------------------------
Intercept                      1.124    0.489  2.299 0.021  0.166  2.083
is_correct[T.True]            -0.292    0.320 -0.914 0.360 -0.919  0.334
confidence                    -0.007    0.004 -1.836 0.066 -0.015  0.000
is_correct[T.True]:confidence  0.007    0.006  1.235 0.217 -0.004  0.018
Group Var                      5.564    0.455
========================================================================

FRONTAL CLUSTER

GRADIOMETERS

times = np.array([21, 22, 22, 23, 23, 24, 24, 25, 25, 26, 26, 27, 27, 28, 28, 28, 29,
       29, 29, 30, 30, 30, 30, 31, 31, 32, 33, 33, 34, 34, 34, 33, 34, 35,
       35, 35, 35, 35, 35, 35, 35, 35, 35, 36, 36, 36, 36, 36, 36, 36, 36,
       36, 37, 37, 37, 37, 37, 37, 37, 37, 38, 38, 38, 38, 38, 38, 38, 39,
       39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 39, 40, 40, 40, 40, 40, 40,
       40, 40, 40, 41, 41, 41, 41, 41, 40, 41, 41, 41, 41, 41, 41, 42, 42,
       42, 42, 42, 42, 42, 42, 42, 42, 43, 43, 43, 43, 43, 43, 43, 44, 44,
       44, 44, 44, 45, 45, 46, 45, 46, 46, 46, 46, 47, 47, 47, 47, 47, 48,
       48, 48, 48, 48, 48, 48, 49, 49, 49, 49, 49, 49, 49, 50, 50, 50, 50,
       50, 50, 49, 50, 50, 51, 51, 51, 51, 51, 51, 51, 51, 52, 52, 52, 52,
       52, 52, 52, 52, 53, 53, 53, 53, 53, 53, 53, 53, 54, 54, 54, 54, 54,
       54, 54, 54, 55, 55, 55, 55, 55, 55, 55, 55, 56, 56, 56, 56, 56, 57,
       57, 57, 57, 58, 58, 58, 59])

grads = np.array([ 22,  18,  22,  18,  22,  18,  22,  18,  22,  18,  22,  18,  22,
         2,  22,  18,   2,  22,  18,   2,  22,  18,  25,   2,  22,  22,
        18,  22,   2,  22,  18,   8,   8,   2,   5,   9,  22,   8,  11,
        18,  25,  14,  31,   2,   5,   9,  22,   8,  11,  13,  14,  31,
         2,   5,   9,  22,   8,  13,  14,  31,   2,  22,   8,  13,  14,
        31,  29,   2,   9,  22,   8,  11,  13,  25,  31,  27,  29,  44,
        75,   9,  11,  18,  22,  25,  13,  31,  29,  75,   9,  11,  18,
        22,  25,  51,  13,  31,  29,  49,  51,  75,   2,   9,  22,  11,
        25,  13,  31,  29,  49,  51,   2,   9,  13,  31,  29,  25,  51,
         2,  25,  27,  44,  31,   2,  31,   2, 109,  13,  15,  31, 109,
        13,  15,  31, 109,  29,   6, 109,  15,  13,  31,  29,  49,   6,
        13,  15,  31,  29,  49,  51,  13,  15,  31,  29,  49,  51,  27,
        25,  27,  13,  31,  29,  44,  49,  27,  51,  25,  13,  15,  31,
        29,  49,  51,  25,  27,  13,  15,  31,  29,  49,  51,  25,  27,
        13,  15,  31,  29,  49,  51,  25,  27,  13,  15,  31,  29,  49,
        51,  25,  27,  25,  29,  31,  49,  51,  25,  29,  31,  49,  25,
        29,  49,  29])
                   Mixed Linear Model Regression Results
===========================================================================
Model:                  MixedLM       Dependent Variable:       target
No. Observations:       2708          Method:                   REML
No. Groups:             28            Scale:                    27457.3555
Min. group size:        60            Log-Likelihood:           -17722.2408
Max. group size:        112           Converged:                Yes
Mean group size:        96.7
---------------------------------------------------------------------------
                               Coef.   Std.Err.   z    P>|z|  [0.025 0.975]
---------------------------------------------------------------------------
Intercept                      -16.652   20.298 -0.820 0.412 -56.436 23.131
is_correct[T.True]               2.281   15.477  0.147 0.883 -28.053 32.615
confidence                      -0.494    0.192 -2.569 0.010  -0.871 -0.117
is_correct[T.True]:confidence    0.092    0.276  0.332 0.740  -0.449  0.632
Group Var                     8884.811   15.126
===========================================================================

MAGNETOMETERS
                 Mixed Linear Model Regression Results
========================================================================
Model:                  MixedLM      Dependent Variable:      target
No. Observations:       2708         Method:                  REML
No. Groups:             28           Scale:                   74.1621
Min. group size:        60           Log-Likelihood:          -9695.7003
Max. group size:        112          Converged:               Yes
Mean group size:        96.7
------------------------------------------------------------------------
                              Coef.  Std.Err.   z    P>|z| [0.025 0.975]
------------------------------------------------------------------------
Intercept                     -0.947    0.639 -1.483 0.138 -2.198  0.305
is_correct[T.True]            -0.446    0.804 -0.555 0.579 -2.021  1.129
confidence                     3.148    0.996  3.161 0.002  1.196  5.100
is_correct[T.True]:confidence  0.234    1.431  0.164 0.870 -2.570  3.039
Group Var                      4.288    0.162
========================================================================

"""
import numpy as np
import pandas as pd
from joblib import Memory
from mne import read_epochs
from tqdm import tqdm
import scipy.stats as st
import matplotlib.pyplot as plt

from mne.io import read_info
import statsmodels.formula.api as smf
import seaborn as sns
from scipy import stats
from statsmodels.stats.diagnostic import het_white
import matplotlib

from metacog import bp
from metacog.config_parser import cfg

location = "./cachedir"
memory = Memory(location, verbose=0)

ch_type = "grad"


@memory.cache
def load_data_clust_av(times, spaces, task="answer"):
    dfs = []
    data = []
    for subj in tqdm(cfg.subjects):
        ep_path = bp.epochs.fpath(subject=subj)
        ep = read_epochs(ep_path)[task]["confidence < 100 and confidence > 0"]
        # ep = read_epochs(ep_path)[task]
        ep.apply_baseline()
        df = ep.metadata.copy()
        tmp = ep.pick_types(meg=ch_type).get_data().transpose([0, 2, 1])
        data.append(tmp[:, times, spaces].mean(axis=1))
        df["subject"] = subj
        dfs.append(df)
    return dfs, data


# clust = np.load("erp_cluster.npz")

clust = np.load("cluster_mag.npz")

# info_src = bp.epochs.fpath(subject="01")
# info = read_info(info_src)
grads = []
times = []
for m, t in zip(clust["spaces"], clust["times"]):
    # grads.append(m * 2)
    grads.append(m * 2 + 1)
    times.append(t)
    # times.append(t)
grads = np.array(grads)
times = np.array(times)

# dfs, data = load_data_clust_av(clust['times'], clust['spaces'])
dfs, data = load_data_clust_av(times, grads)

all_data = np.concatenate(data)
df = pd.concat(dfs)
df["target"] = all_data
df.is_correct = df.is_correct.astype(bool)
if ch_type == "mag":
    df.target *= 1e14
elif ch_type == "grad":
    df.target *= 1e12
df.confidence /= 100
df = df[df.confidence.notna()]

md = smf.mixedlm(
    "target ~ is_correct*confidence",
    data=df,
    groups=df.subject,
    # re_formula="~confidence",
)
mdf = md.fit(method="powell")
print(mdf.summary())

df_sep = df.copy()
df_low = df_sep[df_sep.confidence < 0.4]
df_high = df_sep[df_sep.confidence > 0.6]

# When we don't care about repeated measures, the difference is significant
# print(st.mannwhitneyu(df_low.target, df_high.target, alternative='two-sided'))

av_low = df_low.groupby("subject").target.mean()
av_high = df_high.groupby("subject").target.mean()

anova_data = pd.concat([av_low, av_high], axis=1).to_numpy()

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
    mdf.resid, hist=False, kde_kws={"shade": True, "lw": 1}, fit=stats.norm
)
ax.set_xlabel("Residuals")
plt.show()

labels = ["Statistic", "p-value"]
norm_res = stats.shapiro(mdf.resid)
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
