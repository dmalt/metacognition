"""
ERP no subject average

Cluster-level permutation test on single trials.

Oddly, gradiometers and magnetometers show completely different clusters

Gradiometer cluster is around 300 ms.

"""
import numpy as np
from mne import EpochsArray, pick_types
from mne.io import read_info
from mne import set_log_level
from mne.stats import spatio_temporal_cluster_test
from mne.channels import find_ch_adjacency
import matplotlib
from mne import combine_evoked

from metacog import bp
from metacog.utils import plot_temporal_clusters
from metacog.dataset_specific_utils import (
    assemble_epochs,
    LOW_CONF_EPOCH,
    HIGH_CONF_EPOCH,
)
import matplotlib.pyplot as plt

set_log_level(verbose="ERROR")


# load the data
ch_type = "grad"
X, y = assemble_epochs("answer", ch_type=ch_type)

info_src = bp.epochs.fpath(subject="01")
info = read_info(info_src)
sel_idx = pick_types(info, meg=ch_type)
info.pick_channels([info.ch_names[s] for s in sel_idx])

erf_low = EpochsArray(X[y == LOW_CONF_EPOCH, ...], info, tmin=-1).average()
erf_high = EpochsArray(X[y == HIGH_CONF_EPOCH, ...], info, tmin=-1).average()
erf_low.apply_baseline()
erf_high.apply_baseline()

# erf_diff = combine_evoked([erf_low, -erf_high], weights="equal")
# f1 = erf_low.plot_joint(
#     times=[-1, -0.92, -0.734, 0.132, 0.192, 0.288, 0.4], show=False
# )
# f1.set_size_inches(14, 6)
# plt.title("Low confidence ERF", fontsize=20)
# plt.show()

# f2 = erf_high.plot_joint(
#     times=[-1, -0.92, -0.734, 0.132, 0.192, 0.288, 0.4], show=False
# )
# f2.set_size_inches(14, 6)
# plt.title("High confidence ERF", fontsize=20)

# f3 = erf_diff.plot_joint(times=[0.290], show=False)
# f3.set_size_inches(14, 6)
# plt.title("Difference ERF", fontsize=20)
# plt.show()
# assert False

adjacency, ch_names = find_ch_adjacency(info, ch_type=ch_type)

X_low = X[y == LOW_CONF_EPOCH, ...].transpose(0, 2, 1)
X_high = X[y == HIGH_CONF_EPOCH, ...].transpose(0, 2, 1)

# set cluster threshold
threshold = 6.0
# set family-wise p-value
p_accept = 0.05
cluster_stats = spatio_temporal_cluster_test(
    [X_low, X_high],
    n_permutations=100,
    threshold=threshold,
    tail=0,
    n_jobs=1,
    buffer_size=None,
    adjacency=adjacency,
)

T_obs, clusters, p_values, _ = cluster_stats
good_cluster_inds = np.where(p_values < p_accept)[0]


# organize data for plotting
evokeds = {"low": erf_low, "high": erf_high}


font = {'family' : 'normal',
        'weight' : 'bold',
        'size'   : 15}
matplotlib.rc('font', **font)
plot_temporal_clusters(
    good_cluster_inds, evokeds, T_obs, clusters, erf_low.times, info
)
