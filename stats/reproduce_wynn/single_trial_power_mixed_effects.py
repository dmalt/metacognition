"""
Plan

1) Get sensors selection routine
- Get frontal and parietal gradiometer indices
2) Load erps for single trials
3) Average data in 300-500 frontal and 400-800 parietal ms windows
4) Do mixed linear model
    - prepare condition categorical variable with levels:
        . high conf hit
        . low conf hit
        . miss
    - do mixed linear model for average data ~ condition

"""
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt

from metacog.dataset_specific_utils import assemble_epochs_new
from metacog.group_analysis.reproduce_wynn.utils import prepare_psd
import numpy as np

freq_band = (4, 8)
time_win = (0.4, 0.8)
ch_group = "parietal"
psd_params = dict(fmin=0, fmax=30, n_fft=128)
ch_type = "grad"

X, meta, times, info = assemble_epochs_new(ch_type=ch_type)

df, psd, freqs = prepare_psd(
    times, time_win, ch_group, meta, X, freq_band, info, psd_params
)

print(freqs)
if ch_type == "mag":
    df.data *= 1e14 ** 2
elif ch_type == "grad":
    df.data *= 1e12 ** 2

# df.data = np.log(df.data)  # 
# df.data = stats.boxcox(df.data)[0]
# md = smf.mixedlm("data ~ C(condition, Treatment('HIGH HIT'))", data=df, groups="subject",
#                  # re_formula="~condition"
#                  )
md = smf.mixedlm("data ~ condition", data=df, groups="subject",
                 # re_formula="~condition"
                 )
mdf = md.fit()
print(mdf.summary())

# df = df[df.data < 8]

# md = smf.mixedlm("data ~ confidence * is_correct", data=df,
#                  # re_formula="~ 0 + confidence",
#                  groups="subject")
# mdf = md.fit(method="powell")
# print(mdf.summary())


dd = df.copy()
d_low = psd[dd.condition == "LOW HIT", :, :].mean(axis=(0, 1))
d_high = psd[dd.condition == "HIGH HIT", :, :].mean(axis=(0, 1))
d_low_miss = psd[dd.condition == "LOW MISS", :, :].mean(axis=(0, 1))
d_high_miss = psd[dd.condition == "HIGH MISS", :, :].mean(axis=(0, 1))

plt.plot(freqs, d_low)
plt.plot(freqs, d_high)
plt.plot(freqs, d_low_miss)
plt.plot(freqs, d_high_miss)
plt.legend(["low hit", "high hit", "low miss", "high miss"])
plt.show()

import matplotlib
import scipy.stats as st
from statsmodels.stats.diagnostic import het_white
import seaborn as sns

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
