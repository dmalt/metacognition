import numpy as np
import matplotlib.pyplot as plt
from mne import EpochsArray, pick_types
from mne.io import read_info
from mne import set_log_level
from mne.stats import spatio_temporal_cluster_test
from mne.channels import find_ch_adjacency
from mne.time_frequency import psd_multitaper
from mne.channels.layout import _merge_ch_data

from mne.viz.topomap import (
    plot_psds_topomap,
    _prepare_topomap_plot,
    _make_head_outlines,
)
from metacog import bp
from metacog.utils import plot_temporal_clusters
from metacog.dataset_specific_utils import (
    assemble_epochs,
    LOW_CONF_EPOCH,
    HIGH_CONF_EPOCH,
)


set_log_level(verbose="ERROR")


ch_type = "grad"
# load the data
X, y = assemble_epochs("answer")  # dict with subj -> epochs mapping

info_src = bp.epochs.fpath(subject="01")
info = read_info(info_src)
sel_idx = pick_types(info, meg="grad")
info.pick_channels([info.ch_names[s] for s in sel_idx])

ep_low = EpochsArray(X[y == LOW_CONF_EPOCH, ...], info, tmin=-1)
ep_high = EpochsArray(X[y == HIGH_CONF_EPOCH, ...], info, tmin=-1)
# erf_diff = combine_evoked([ep_low, -ep_high], weights="equal")

psds_high, freqs = psd_multitaper(ep_high, tmin=0, tmax=1, fmax=50)
psds_low, freqs = psd_multitaper(ep_low, tmin=0, tmax=1, fmax=50)

theta_mask = np.logical_and(4 <= freqs, freqs < 8)
theta_power_low = psds_low[:, :, theta_mask].mean(axis=2)
theta_power_high = psds_high[:, :, theta_mask].mean(axis=2)

(
    picks,
    pos,
    merge_channels,
    names,
    ch_type,
    sphere,
    clip_origin,
) = _prepare_topomap_plot(ep_low, ch_type, sphere=None)
outlines = _make_head_outlines(sphere, pos, "head", clip_origin)

psds = (psds_high.mean(axis=0) - psds_low.mean(axis=0)) / psds_low.mean(axis=0)
if merge_channels:
    psds_merge, names = _merge_ch_data(psds, ch_type, names, method="mean")

fig = plot_psds_topomap(
    psds_merge,
    freqs,
    dB=False,
    # vlim=(1, 1.5),
    bands=[
        (2, 4, "delta (2-4)"),
        (4, 8, "theta (4-8)"),
        (8, 12, "alpha (8-12)"),
        (12, 30, "beta (12-30)"),
    ],
    pos=pos,
    outlines=outlines,
    sphere=sphere,
    show=False,
)
fig.set_size_inches((20, 10))
plt.show()

adjacency, ch_names = find_ch_adjacency(info, ch_type="grad")
# set cluster threshold
threshold = 10.0  # very high, but the test is quite sensitive on this data
# set family-wise p-value
p_accept = 0.05

# X_low = X[y == LOW_CONF_EPOCH, ...].transpose(0, 2, 1)
# X_high = X[y == HIGH_CONF_EPOCH, ...].transpose(0, 2, 1)
cluster_stats = spatio_temporal_cluster_test(
    [theta_power_low[:, np.newaxis, :], theta_power_high[:, np.newaxis, :]],
    n_permutations=100,
    threshold=threshold,
    tail=1,
    n_jobs=1,
    buffer_size=None,
    adjacency=adjacency,
)

T_obs, clusters, p_values, _ = cluster_stats
good_cluster_inds = np.where(p_values < p_accept)[0]


# organize data for plotting
evokeds = {"low": erf_low, "high": erf_high}


plot_temporal_clusters(
    good_cluster_inds, evokeds, T_obs, clusters, erf_low.times, info
)
