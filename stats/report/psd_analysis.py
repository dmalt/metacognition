"""PSD analysis on single trial, no repeated measures control

Some kinda strange significant clusters in low and high beta
"""
import numpy as np
import matplotlib.pyplot as plt
from mne.io import read_info
from mne import EpochsArray, pick_types, EvokedArray
from mne.stats import spatio_temporal_cluster_test
from mne.channels import find_ch_adjacency

from mne.viz.topomap import (
    plot_psds_topomap,
    _prepare_topomap_plot,
    _make_head_outlines,
)
from mne.channels.channels import _get_ch_type
from mne.defaults import _handle_default
from mne.channels.layout import _merge_ch_data

from mne.time_frequency import psd_multitaper, psd_welch

from mne.viz import plot_compare_evokeds, tight_layout
from mpl_toolkits.axes_grid1 import make_axes_locatable

from metacog import bp
from metacog.dataset_specific_utils import (
    assemble_epochs,
    LOW_CONF_EPOCH,
    HIGH_CONF_EPOCH,
)

ch_type = "grad"
X, y = assemble_epochs("answer", ch_type=ch_type)  # dict with subj -> epochs mapping

info_src = bp.epochs.fpath(subject="01")
info = read_info(info_src)
sel_idx = pick_types(info, meg=ch_type)
info.pick_channels([info.ch_names[s] for s in sel_idx])

# create epochs objects
ep_low = EpochsArray(X[y == LOW_CONF_EPOCH, ...], info, tmin=-1)
ep_high = EpochsArray(X[y == HIGH_CONF_EPOCH, ...], info, tmin=-1)

# psds_high, freqs = psd_multitaper(ep_high, tmin=0, tmax=1, fmax=50)
# psds_low, freqs = psd_multitaper(ep_low, tmin=0, tmax=1, fmax=50)
psds_high, freqs = psd_welch(ep_high, tmin=0.3, tmax=0.9, fmax=50)
psds_low, freqs = psd_welch(ep_low, tmin=0.3, tmax=0.9, fmax=50)

# normalize
# psds_high /= psds_high.mean(axis=2, keepdims=True)
# psds_low /= psds_low.mean(axis=2, keepdims=True)

psds = (psds_high.mean(axis=0) - psds_low.mean(axis=0)) / psds_low.mean(axis=0)
ch_type = _get_ch_type(ep_high, None)
units = _handle_default("units", None)
unit = units[ch_type]

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

if merge_channels:
    psds_merge, names = _merge_ch_data(psds, ch_type, names, method="mean")
else:
    psds_merge = psds

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

adjacency, ch_names = find_ch_adjacency(info, ch_type=ch_type)
# set cluster threshold
threshold = 6.0  # very high, but the test is quite sensitive on this data
# set family-wise p-value
p_accept = 0.05


psds_low_t = psds_low.transpose(0, 2, 1)
psds_high_t = psds_high.transpose(0, 2, 1)

cluster_stats = spatio_temporal_cluster_test(
    [psds_low_t, psds_high_t],
    n_permutations=500,
    threshold=threshold,
    tail=1,
    n_jobs=8,
    buffer_size=None,
    adjacency=adjacency,
)

T_obs, clusters, p_values, _ = cluster_stats
good_cluster_inds = np.where(p_values < p_accept)[0]
colors = {"low": "crimson", "high": "steelblue"}
linestyles = {"low": "-", "high": "--"}

# organize data for plotting
info['sfreq'] = len(freqs) / freqs[-1]
evokeds = {
    "low": EvokedArray(psds_low.mean(0), info, tmin=freqs[0]),
    "high": EvokedArray(psds_high.mean(0), info, tmin=freqs[0]),
}

#
# loop over clusters
for i_clu, clu_idx in enumerate(good_cluster_inds):
    # unpack cluster information, get unique indices
    time_inds, space_inds = np.squeeze(clusters[clu_idx])
    ch_inds = np.unique(space_inds)
    time_inds = np.unique(time_inds)

    # get topography for F stat
    f_map = T_obs[time_inds, ...].mean(axis=0)

    # get signals at the sensors contributing to the cluster
    sig_times = freqs[time_inds]

    # create spatial mask
    mask = np.zeros((f_map.shape[0], 1), dtype=bool)
    mask[ch_inds, :] = True

    # initialize figure
    fig, ax_topo = plt.subplots(1, 1, figsize=(10, 3))

    # plot average test statistic and mark significant sensors
    f_evoked = EvokedArray(f_map[:, np.newaxis], info, tmin=0)
    f_evoked.plot_topomap(
        times=0,
        mask=mask,
        axes=ax_topo,
        cmap="Reds",
        vmin=np.min,
        vmax=np.max,
        show=False,
        colorbar=False,
        mask_params=dict(markersize=10),
    )
    image = ax_topo.images[0]

    # create additional axes (for ERF and colorbar)
    divider = make_axes_locatable(ax_topo)

    # add axes for colorbar
    ax_colorbar = divider.append_axes("right", size="5%", pad=0.05)
    plt.colorbar(image, cax=ax_colorbar)
    ax_topo.set_xlabel(
        "Averaged F-map ({:0.3f} - {:0.3f} s)".format(*sig_times[[0, -1]])
    )

    # add new axis for time courses and plot time courses
    ax_signals = divider.append_axes("right", size="300%", pad=1.2)
    title = "Cluster #{0}, {1} sensor".format(i_clu + 1, len(ch_inds))
    if len(ch_inds) > 1:
        title += "s (mean)"
    plot_compare_evokeds(
        evokeds,
        title=title,
        picks=ch_inds,
        axes=ax_signals,
        colors=colors,
        linestyles=linestyles,
        show=False,
        split_legend=True,
        truncate_yaxis="auto",
    )

    # plot temporal cluster extent
    ymin, ymax = ax_signals.get_ylim()
    ax_signals.fill_betweenx(
        (ymin, ymax), sig_times[0], sig_times[-1], color="orange", alpha=0.3
    )

    # clean up viz
    tight_layout(fig=fig)
    fig.subplots_adjust(bottom=0.05)
    plt.show()
