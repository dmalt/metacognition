from tqdm import tqdm
import numpy as np
from mne import read_epochs, combine_evoked, pick_types
from mne.io import read_info
from mne.stats import spatio_temporal_cluster_test
from mne.channels import find_ch_adjacency
from config import bp_epochs, subjects
from utils import plot_temporal_clusters
import matplotlib.pyplot as plt

LOW_CONF_EPOCH = 24
HIGH_CONF_EPOCH = 44
ep_type = "answer"
n_channels = 204
n_times = 1001

info_src = bp_epochs.fpath(subject="01")
info = read_info(info_src)
adjacency, ch_names = find_ch_adjacency(info, ch_type="grad")
X = np.empty((0, n_channels, n_times))
y = np.empty(0)
for subj in tqdm(subjects[1:], desc="Loading epochs"):
    ep_path = bp_epochs.fpath(subject=subj)
    ep = (
        read_epochs(ep_path)
        .interpolate_bads()
        .pick_types(meg="grad")[ep_type]
    )
    ep.apply_baseline()

    # required to merge epochs from differen subjects together
    ep.info["dev_head_t"] = None
    X_low = ep["low"].get_data().transpose([0, 2, 1])
    y_low = ep["low"].events[:, 2]
    X_high = ep["high"].get_data().transpose([0, 2, 1])
    y_high = ep["high"].events[:, 2]

    erf_low = ep["low"].average()
    erf_high = ep["high"].average()
    erf_diff = combine_evoked([erf_low, -erf_high], weights="equal")

    f1 = erf_low.plot_joint(
        times=[-1, -0.92, -0.734, 0.132, 0.192, 0.288, 0.4], show=False
    )
    f1.set_size_inches(14, 6)
    plt.title("Low confidence ERF", fontsize=20)

    f2 = erf_high.plot_joint(
        times=[-1, -0.92, -0.734, 0.132, 0.192, 0.288, 0.4], show=False
    )
    f2.set_size_inches(14, 6)
    plt.title("High confidence ERF", fontsize=20)

    f3 = erf_diff.plot_joint(times=[0.290], show=False)
    f3.set_size_inches(14, 6)
    plt.title("Difference ERF", fontsize=20)
    plt.show()
    p_accept = 0.05
    cluster_stats = spatio_temporal_cluster_test(
        [X_low, X_high],
        n_permutations=100,
        # threshold=threshold,
        tail=0,
        n_jobs=1,
        buffer_size=None,
        adjacency=adjacency,
    )

    T_obs, clusters, p_values, _ = cluster_stats
    good_cluster_inds = np.where(p_values < p_accept)[0]

    # organize data for plotting
    evokeds = {"low": erf_low, "high": erf_high}


    sel_idx = pick_types(info, meg="grad")
    info.pick_channels([info.ch_names[s] for s in sel_idx])
    plot_temporal_clusters(
        good_cluster_inds, evokeds, T_obs, clusters, erf_low.times, info
    )
