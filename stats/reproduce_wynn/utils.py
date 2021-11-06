from itertools import product

import numpy as np
from mne.selection import read_selection
from mne.time_frequency import psd_array_welch
import pandas as pd


def add_condition(meta, c_lo, c_hi):
    df = meta.copy()
    df["condition"] = "MISS"
    # df.loc[(df.confidence <= c_lo), "condition"] = "LOW MISS"
    # df.loc[(df.confidence >= c_hi), "condition"] = "HIGH MISS"
    df.loc[(df.confidence <= c_lo) & df.is_correct, "condition"] = "LOW HIT"
    df.loc[(df.confidence >= c_hi) & df.is_correct, "condition"] = "HIGH HIT"
    df.condition = df.condition.astype("category")
    df.is_correct = df.is_correct.astype(bool)
    return df


def prepare_psd(times, t_win, ch_group, meta, X, freq_band, info, psd_params):
    """
    df.data is average PSD across ch_group and times between t_lo and t_hi
    psd is non-averaged PSD returned for plotting/inspection

    """
    df, X = _drop_by_confidence(meta, X, 0, 30, 70, 100)
    df = add_condition(df, 30, 70)

    time_mask, ch_inds = _get_masks(times, t_win[0], t_win[1], ch_group, info)
    psd, freqs = psd_array_welch(
        X[:, ch_inds, time_mask], sfreq=info["sfreq"], **psd_params
    )

    freq_mask = np.logical_and(freqs > freq_band[0], freqs < freq_band[1])
    df["data"] = psd[:, :, freq_mask].mean(axis=(1, 2))

    return df, psd, freqs


def prepare_band_power(times, t_win, meta, X, freq_band, info, psd_params):
    """
    df.data is average PSD across ch_group and times between t_lo and t_hi
    psd is non-averaged PSD returned for plotting/inspection

    """
    df, X = _drop_by_confidence(meta, X, 0, 30, 70, 100)
    df = add_condition(df, 30, 70)

    time_mask, _ = _get_masks(times, t_win[0], t_win[1], "parietal", info)
    psd, freqs = psd_array_welch(
        X[:, :, time_mask.squeeze()], sfreq=info["sfreq"], **psd_params
    )
    # freq_mask = np.logical_and(freqs > freq_band[0], freqs < freq_band[1])
    # power = (
    #     psd[:, :, freq_mask].mean(axis=2, keepdims=True).transpose((0, 2, 1))
    # )
    power = psd.transpose((0, 2, 1))

    return df, power, freqs


def prepare_erp(times, t_win, ch_group, meta, X, info):
    time_mask, ch_inds = _get_masks(times, t_win[0], t_win[1], ch_group, info)
    df, data = _drop_by_confidence(meta, X, 0, 30, 70, 100)
    df = add_condition(df, 30, 70)
    subj_data = []
    av_df_data = []
    for subj, cond in product(np.unique(df.subject), np.unique(df.condition)):
        mask = np.logical_and(df.subject == subj, df.condition == cond)
        data_sel = data[mask, ...]
        subj_data.append(
            data_sel[:, np.squeeze(ch_inds), :].mean(axis=0, keepdims=True)
        )
        av_df_data.append((data_sel[:, ch_inds, time_mask].mean(), subj, cond))
    return (
        pd.DataFrame(av_df_data, columns=("data", "subj", "cond")),
        np.concatenate(subj_data),
    )


def prepare_erp_new(times, t_win, ch_group, meta, X, info):
    time_mask, ch_inds = _get_masks(times, t_win[0], t_win[1], ch_group, info)
    df, data = _drop_by_confidence(meta, X, 0, 30, 70, 100)
    df = add_condition(df, 30, 70)
    subj_data = []
    av_df_data = []
    for subj, cond in product(np.unique(df.subject), np.unique(df.condition)):
        mask = np.logical_and(df.subject == subj, df.condition == cond)
        data_sel = data[mask, ...]
        d = data_sel[:, np.squeeze(ch_inds), time_mask].mean(axis=(1, 2))
        subj_data.append(d)
        av_df_data.append(d, subj, cond)
    return (
        pd.DataFrame(av_df_data, columns=("data", "subj", "cond")),
        np.concatenate(subj_data),
    )


def _drop_by_confidence(df, data, c1, c2, c3, c4):
    df_cp = df.copy()
    c = df.confidence
    conf_mask = ((c <= c2) & (c > c1)) | ((c >= c3) & (c < c4))
    return df_cp[conf_mask], data[conf_mask, ...]


def _get_masks(times, t_lo, t_hi, ch_group, info):
    time_mask = np.logical_and(times >= t_lo, times < t_hi).nonzero()[0][
        np.newaxis, :
    ]
    ch_names = [s.replace(" ", "") for s in read_selection(ch_group)]
    ch_inds = np.array(
        [i for i, c in enumerate(info["ch_names"]) if c in ch_names]
    )[:, np.newaxis]
    return time_mask, ch_inds


if __name__ == "__main__":
    from metacog.dataset_specific_utils import assemble_epochs_new

    X, meta, times, info = assemble_epochs_new()
    df, data = prepare_erp(times, (0.4, 0.8), "parietal", meta, X, info)
