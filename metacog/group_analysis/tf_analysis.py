import pandas as pd

import statsmodels.api as sm
import statsmodels.formula.api as smf
from joblib import Memory

from mne.time_frequency import read_tfrs
from metacog import bp
from metacog.config_parser import cfg

location = "./cachedir"
memory = Memory(location, verbose=0)


@memory.cache
def load_data(band):
    band = "beta"
    dfs = []
    data = []
    for subj in cfg.subjects:
        tfr_path = bp.tfr_av.fpath(subject=subj, acquisition=band)
        tfr = read_tfrs(tfr_path)[0]["confidence < 100 and confidence > 0"]
        df = tfr.metadata.copy()
        data.append(tfr.pick_types(meg="grad").data[:, :, 0, :])
        df["subject"] = subj
        dfs.append(df)
    return dfs, data


def make_cumulative_df(dfs, data, ch_ind, time_ind):
    dfs_with_data = []
    scaling_factor = 1e24
    for subj_data, subj_df in zip(data, dfs):
        new_df = subj_df.copy()
        new_df["data"] = subj_data[:, ch_ind, time_ind] * scaling_factor
        dfs_with_data.append(new_df)
    cumulative_df = pd.concat(dfs_with_data, ignore_index=True)
    cumulative_df.is_correct = cumulative_df.is_correct.astype(bool)
    return cumulative_df


# subjects = ["04", "05"]
band = "beta"
time_ind = 1
ch_ind = 1


for ch_ind in range(204):
    dfs, data = load_data(band)
    cumulative_df = make_cumulative_df(dfs, data, ch_ind, time_ind)

    # info_src = bp_epochs.fpath(subject="01")
    # info = read_info(info_src)
    # sel_idx = pick_types(info, meg="grad")

    md = smf.mixedlm(
        "data ~ is_correct + confidence",
        data=cumulative_df,
        groups=cumulative_df["subject"],
    )
    mdf = md.fit()
    sum = mdf.summary()
    is_corr_p = sum.tables[1]["P>|z|"]["is_correct[T.True]"]
    conf_p = sum.tables[1]["P>|z|"]["confidence"]

    if float(is_corr_p) < 0.05 or float(conf_p) < 0.05:
        print("!!!!!!!!!!!!!!!!!!!!")
    print(
        f"ch_ind={ch_ind}, time_ind={time_ind}:: corr_p={is_corr_p}, conf_p={conf_p}"
    )



# diff_tfr = avg_low.copy()
# # diff_tfr.data = (avg_high.data - avg_low.data) / avg_low.data
# diff_tfr.data = (avg_high.data) / avg_low.data
# fig = diff_tfr.plot_topo(show=False, vmin=0.5, vmax=2)
# fig.set_size_inches((20, 10))
# plt.show()

# sen = diff_tfr.ch_names.index('MEG2643')
# fig = diff_tfr.plot(
#     [sen],
#     title=diff_tfr.ch_names[sen] + " (high - low)",
#     show=False,
#     vmin=-1,
#     vmax=1,
# )
# fig.set_size_inches(20, 4)
# plt.show()
