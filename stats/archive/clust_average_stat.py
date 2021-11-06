import numpy as np
import pandas as pd
from joblib import Memory
from mne import read_epochs
from tqdm import tqdm
import scipy.stats as st
from mne.stats import f_mway_rm

import statsmodels.api as sm
import statsmodels.formula.api as smf

from config import subjects, bp_epochs

location = "./cachedir"
memory = Memory(location, verbose=0)


@memory.cache
def load_data_clust_av(times, spaces, task="answer"):
    dfs = []
    data = []
    for subj in tqdm(subjects):
        ep_path = bp_epochs.fpath(subject=subj)
        ep = read_epochs(ep_path)[task]["confidence < 100 and confidence > 0"]
        # ep = read_epochs(ep_path)[task]
        ep.apply_baseline()
        df = ep.metadata.copy()
        tmp = ep.pick_types(meg="grad").get_data().transpose([0, 2, 1])
        data.append(tmp[:, times, spaces].mean(axis=1))
        df["subject"] = subj
        dfs.append(df)
    return dfs, data


clust = np.load("erp_cluster.npz")
dfs, data = load_data_clust_av(clust['times'], clust['spaces'])

all_data = np.concatenate(data)
df = pd.concat(dfs)
df['target'] = all_data
df.is_correct = df.is_correct.astype(bool)
df.target *= 1e12
df = df[df.confidence.notna()]
# df.confidence /= 100
# df.confidence -= df.confidence.mean()
# df.target = st.boxcox(df.target - df.target.min() * 1.01)[0]
# df.target=st.boxcox(df.target - df.target.min() * 1.01, lmbda=1)

st.spearmanr(df.confidence, df.target)
st.kendalltau(df.is_correct, df.target)
st.pearsonr(df.confidence, df.target)

md = smf.mixedlm(
    "target ~ is_correct*confidence",
    data=df,
    groups=df.subject,
    # re_formula="~confidence",
)
mdf = md.fit(method="powell")
mdf.summary()

df_sep = df.copy()
df_low = df_sep[df_sep.confidence < 40]
df_high = df_sep[df_sep.confidence > 50]

st.mannwhitneyu(df_low.target, df_high.target, alternative='greater')
df_low['level'] = np.zeros_like(df_low.target, dtype=bool)
df_high['level'] = np.ones_like(df_high.target, dtype=bool)

ll = pd.concat([df_low, df_high])

md = smf.mixedlm(
    "target ~ confidence*is_correct",
    data=df,
    groups=df["subject"],
    # re_formula="~is_correct",
)
mdf = md.fit(method="powell")
mdf.summary()

av_low = df_low.groupby("subject").target.mean()
av_high = df_high.groupby("subject").target.mean()

# anova_data = pd.concat([av_low, av_high], axis=1).to_numpy()

# import seaborn as sns
# import matplotlib.pyplot as plt
# sns.catplot(data=df, kind="bar", x="confidence", y="target", hue="is_correct")
# plt.show()

# sns.jointplot(data=df, x="confidence", y="subject", hue="is_correct")


# fig = plt.figure()
# ax = fig.add_subplot(111)
# st.probplot(df.target, plot=ax)
# plt.show()
