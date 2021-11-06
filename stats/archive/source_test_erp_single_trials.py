from config import DERIVATIVES_DIR, subjects, SUBJECTS_DIR
import numpy as np
from joblib import Memory
import pandas as pd
from mne import read_labels_from_annot, read_source_spaces
from mne.stats import spatio_temporal_cluster_test
import os
from scipy.sparse import coo_matrix
from tqdm import tqdm

memory = Memory(location="./cachedir", verbose=0)

SOURCES_LABEL_AV = DERIVATIVES_DIR / "sources_label_av"
SOURCES_PSD_DIR = DERIVATIVES_DIR / "sources_epochs"


@memory.cache
def load_source_data():
    X = []
    dfs = []
    for subj in tqdm(subjects):
        df = pd.read_pickle(
            SOURCES_PSD_DIR / f"sub-{subj}" / f"sub-{subj}_df.pkl"
        )
        df["subject"] = subj
        dfs.append(df)
        subj_dir = SOURCES_LABEL_AV / f"sub-{subj}"
        for fpath in sorted(subj_dir.glob("*.npy")):
            X.append(np.load(fpath))
    return (np.stack(X), pd.concat(dfs))


def get_label_adjacency(parc="aparc.a2009s", dist=0.025):
    labels = read_labels_from_annot(
        "fsaverage", subjects_dir=SUBJECTS_DIR, parc=parc
    )
    src_path = SUBJECTS_DIR / "fsaverage/bem/fsaverage-oct-6-src.fif"
    src = read_source_spaces(src_path)
    os.environ["SUBJECTS_DIR"] = str(SUBJECTS_DIR)
    cms = [{"hemi": lab.hemi, "ind": lab.center_of_mass()} for lab in labels]
    my_src = {"lh": src[0], "rh": src[1]}
    cm_coord = np.stack([my_src[cm["hemi"]]["rr"][cm["ind"], :] for cm in cms])
    dists = (cm_coord[:, np.newaxis, :] - cm_coord[np.newaxis, :, :]) ** 2
    dists = np.sqrt(dists.sum(axis=2))
    np.fill_diagonal(dists, np.inf)

    return coo_matrix(dists < dist), labels


if __name__ == "__main__":
    X, dfs = load_source_data()
    conf_mask = np.logical_and(dfs.confidence > 0, dfs.confidence < 100)
    X = X[conf_mask, :, :]
    dfs = dfs[conf_mask]
    low_mask = dfs.confidence < 40
    high_mask = dfs.confidence > 60
    X_low = X[low_mask, :, :].transpose(0, 2, 1)
    X_high = X[high_mask, :, :].transpose(0, 2, 1)
    adj, labels = get_label_adjacency()

    cluster_stats = spatio_temporal_cluster_test(
        [X_low, X_high], adjacency=adj, n_permutations=100, threshold=6
    )
    T_obs, clusters, p_values, _ = cluster_stats
    thresh = 0.05
    good_cluster_inds = (p_values < thresh).nonzero()[0]

    times = np.arange(-1, 1.002, 0.002)
    for g in good_cluster_inds:
        print("-" * 80)
        lab_inds = np.unique(clusters[g][1])
        time_inds = np.unique(clusters[g][0])
        for lb in lab_inds:
            print(labels[lb].name)
        print([int(times[t] * 1000) for t in time_inds])


