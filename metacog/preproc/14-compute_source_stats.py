import numpy as np
from mne import read_source_estimate, read_source_spaces, spatial_src_adjacency
from mne.stats import (
    summarize_clusters_stc, spatio_temporal_cluster_test, ttest_ind_no_p,
)

from metacog.paths import dirs
from metacog.config_parser import cfg

# stcs_low = []
# stcs_high = []
src_path = dirs.fsf_subjects / "fsaverage/bem/fsaverage-oct-6-src.fif"
src = read_source_spaces(src_path)

is_first_iter = True
subj_paths = [dirs.sources / f"sub-{s}" for s in cfg.subjects]
# subj_paths = sorted(dirs.sources.iterdir())
n_subjects = len(subj_paths)
stcs = []
stcs_low = []
stcs_high = []

X_high = []  # high confidence
X_low = []  # low confidence
for trial_path in dirs.sources.glob("*/*.stc"):
    if trial_path.match("*cond-high*"):
        X_high.append(
            read_source_estimate(str(trial_path)[: -len("-rh.stc")]).data.T
        )
    elif trial_path.match("*cond-low*"):
        X_low.append(
            read_source_estimate(str(trial_path)[: -len("-rh.stc")]).data.T
        )
    else:
        print(f"NO MATCH FOR {trial_path}")

X_high = np.array(X_high)
X_low = np.array(X_low)

print("X_high.shape = ", X_high.shape)
print("X_low.shape = ", X_low.shape)

adjacency = spatial_src_adjacency(src)

thresh_pv = 0.02
F_obs, clusters, cluster_pv, H0 = clu = spatio_temporal_cluster_test(
    [X_high, X_low],
    # threshold=8,
    n_permutations=100,
    adjacency=adjacency,
    out_type="indices",
    check_disjoint=True,
    stat_fun=ttest_ind_no_p,
)

stc_all_cluster_vis = summarize_clusters_stc(
    clu,
    p_thresh=thresh_pv,
    # p_thresh=0.05,
    vertices=src,
    subject="fsaverage",
)
stc_all_cluster_vis

stc_all_cluster_vis.plot(subjects_dir=dirs.fsf_subjects, hemi="both")

# good_ids = np.where(cluster_pv < thresh_pv)[0]

# for good_id in good_ids:
#     print(freqs[np.unique(clusters[good_id][0])])



