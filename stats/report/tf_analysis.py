"""Initially """
import pandas as pd
import statsmodels.formula.api as smf
from joblib import Memory
from mne.time_frequency import read_tfrs

from metacog import bp
from metacog.config_parser import cfg

location = "./cachedir"
memory = Memory(location, verbose=0)


@memory.cache
def load_data(band):
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
    """Create metadata with data for selected channel and time index"""
    dfs_with_data = []
    scaling_factor = 1e24
    for subj_data, subj_df in zip(data, dfs):
        new_df = subj_df.copy()
        new_df["data"] = subj_data[:, ch_ind, time_ind] * scaling_factor
        dfs_with_data.append(new_df)
    cumulative_df = pd.concat(dfs_with_data, ignore_index=True)
    cumulative_df.is_correct = cumulative_df.is_correct.astype(bool)
    # cumulative_df.confidence = cumulative_df.confidence.astype("category")
    return cumulative_df


if __name__ == "__main__":

    import numpy as np
    # cfg.subjects = ["04", "05"]
    band = "alphabeta"
    time_ind = 100
    ch_ind = 1

    dfs, data = load_data(band)
    all_data = np.concatenate(data)
    all_dfs = pd.concat(dfs)
    # all_dfs.is_correct = all_dfs.is_correct.astype(bool)

    # np.save(f"data_{band}", all_data)

    # from time import time
    # t1 = time()
    # cumulative_df = make_cumulative_df(dfs, data, ch_ind, time_ind)
    # for ch_ind in range(204):

    #     # info_src = bp_epochs.fpath(subject="01")
    #     # info = read_info(info_src)
    #     # sel_idx = pick_types(info, meg="grad")

    #     md = smf.mixedlm(
    #         "data ~ is_correct * confidence",
    #         data=cumulative_df,
    #         groups=cumulative_df["subject"],
    #     )
    #     mdf = md.fit()
    #     sum = mdf.summary()
    #     is_corr_p = sum.tables[1]["P>|z|"]["is_correct[T.True]"]
    #     conf_p = sum.tables[1]["P>|z|"]["confidence"]

    #     if float(is_corr_p) < 0.05 or float(conf_p) < 0.05:
    #         print("!!!!!!!!!!!!!!!!!!!!")
    #     print(
    #         f"ch_ind={ch_ind}, time_ind={time_ind}:: corr_p={is_corr_p}, conf_p={conf_p}"
    #     )

    # t2 = time()
    # print(t2 - t1)


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


    # import numpy as np
    # mask = np.random.binomial(size=len(cumulative_df), n=1, p=0.5).astype(bool)
    # mask = np.ones_like(d).astype(bool)
    # mask[:len(mask) // 2] = False
    # d = cumulative_df.data.values
    # d[mask] *= -1
    # cumulative_df.data = d
    # md = smf.mixedlm(
    #     "data ~ is_correct * confidence",
    #     data=cumulative_df,
    #     groups=cumulative_df["subject"],
    # )
    # mdf = md.fit()
    # sum = mdf.summary()
