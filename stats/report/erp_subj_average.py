"""
Permutation cluster 1-samp t-test for average ERPs

Compute evoked response for each subject and do the cluster stats.
No significance here

For magnetometers there's marginaly significant cluster (p=0.09) at the same
space-time points as for no-repeated-measures-correction test
"""
import numpy as np
import matplotlib.pyplot as plt
from mne import EpochsArray, combine_evoked, pick_types, EvokedArray
from mne.io import read_info
from mne.viz import plot_compare_evokeds, tight_layout
# from mne import set_log_level
# from mne.stats import spatio_temporal_cluster_test
from mne.stats import spatio_temporal_cluster_1samp_test
from mne.channels import find_ch_adjacency
from mpl_toolkits.axes_grid1 import make_axes_locatable

from metacog import bp
from metacog.dataset_specific_utils import (
    assemble_epochs,
    LOW_CONF_EPOCH,
    HIGH_CONF_EPOCH,
)


# set_log_level(verbose="ERROR")

ch_type = "mag"
# load the data
X, y = assemble_epochs("answer", True, ch_type=ch_type)

info_src = bp.epochs.fpath(subject="01")
info = read_info(info_src)
sel_idx = pick_types(info, meg=ch_type)
info.pick_channels([info.ch_names[s] for s in sel_idx])

erf_low = EpochsArray(X[y == LOW_CONF_EPOCH, ...], info, tmin=-1).average()
erf_high = EpochsArray(X[y == HIGH_CONF_EPOCH, ...], info, tmin=-1).average()
erf_diff = combine_evoked([erf_low, -erf_high], weights="equal")

adjacency, ch_names = find_ch_adjacency(info, ch_type=ch_type)
# set cluster threshold
# threshold = 1.0
# set family-wise p-value
# p_accept = 0.05
p_accept = 0.14

X_low = X[y == LOW_CONF_EPOCH, ...].transpose(0, 2, 1)
X_high = X[y == HIGH_CONF_EPOCH, ...].transpose(0, 2, 1)
X_diff = X_high - X_low

cluster_stats = spatio_temporal_cluster_1samp_test(
    X_diff,
    n_permutations=100,
    # threshold=threshold,
    # tail=1,
    n_jobs=1,
    # buffer_size=None,
    adjacency=adjacency,
)

T_obs, clusters, p_values, _ = cluster_stats
good_cluster_inds = np.where(p_values < p_accept)[0]


colors = {"low": "crimson", "high": 'steelblue'}
linestyles = {"low": '-', "high": '--'}

# organize data for plotting
evokeds = {"low": erf_low, "high": erf_high}

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
    sig_times = erf_low.times[time_inds]

    # create spatial mask
    mask = np.zeros((f_map.shape[0], 1), dtype=bool)
    mask[ch_inds, :] = True

    # initialize figure
    fig, ax_topo = plt.subplots(1, 1, figsize=(10, 3))

    # plot average test statistic and mark significant sensors
    f_evoked = EvokedArray(f_map[:, np.newaxis], info, tmin=0)
    f_evoked.plot_topomap(times=0, mask=mask, axes=ax_topo,
                          vmin=np.min, vmax=np.max, ch_type="mag",
                          show=False,
                          colorbar=False, mask_params=dict(markersize=10))
    image = ax_topo.images[0]

    # create additional axes (for ERF and colorbar)
    divider = make_axes_locatable(ax_topo)

    # add axes for colorbar
    ax_colorbar = divider.append_axes('right', size='5%', pad=0.05)
    plt.colorbar(image, cax=ax_colorbar)
    ax_topo.set_xlabel(
        'Averaged F-map ({:0.3f} - {:0.3f} s)'.format(*sig_times[[0, -1]]))

    # add new axis for time courses and plot time courses
    ax_signals = divider.append_axes('right', size='300%', pad=1.2)
    title = 'Cluster #{0}, {1} sensor'.format(i_clu + 1, len(ch_inds))
    if len(ch_inds) > 1:
        title += "s (mean)"
    plot_compare_evokeds(evokeds, title=title, picks=ch_inds, axes=ax_signals,
                         colors=colors, linestyles=linestyles, show=False,
                         split_legend=True, truncate_yaxis='auto')

    # plot temporal cluster extent
    ymin, ymax = ax_signals.get_ylim()
    ax_signals.fill_betweenx((ymin, ymax), sig_times[0], sig_times[-1],
                             color='orange', alpha=0.3)

    # clean up viz
    tight_layout(fig=fig)
    fig.subplots_adjust(bottom=.05)
    plt.show()
