"""Source-level psd stats on single trials, no repeated measures

Significant cluster is weird.

G_Ins_lg_and_S_cent_ins-lh
G_and_S_frontomargin-lh
G_and_S_subcentral-lh
G_and_S_transv_frontopol-lh
G_cuneus-lh
G_insular_short-lh
G_oc-temp_lat-fusifor-lh
G_oc-temp_med-Lingual-lh
G_oc-temp_med-Parahip-lh
G_occipital_middle-lh
G_pariet_inf-Angular-lh
G_temp_sup-G_T_transv-lh
G_temp_sup-Lateral-lh
G_temp_sup-Plan_tempo-lh
G_temporal_inf-lh
Lat_Fis-ant-Vertical-lh
Lat_Fis-post-lh
Pole_occipital-lh
S_calcarine-lh
S_circular_insula_sup-lh
S_collat_transv_ant-lh
S_collat_transv_post-lh
S_front_inf-lh
S_interm_prim-Jensen-lh
S_oc-temp_med_and_Lingual-lh
S_oc_sup_and_transversal-lh
S_occipital_ant-lh
S_orbital-H_Shaped-lh
S_orbital_lateral-lh
S_precentral-inf-part-lh
S_suborbital-lh
S_temporal_inf-lh
S_temporal_transverse-lh

[-313, -311, -309, -307, -305, -303, -301, -299, -297, -295, -293, -291, -289,
-287, -285, -283, -281, -279, -277, -275, -273]

"""
import numpy as np
from joblib import Memory
import pandas as pd
from mne import read_labels_from_annot, read_source_spaces
from mne.stats import spatio_temporal_cluster_test
import os
from scipy.sparse import coo_matrix
from tqdm import tqdm

from metacog.paths import dirs
from metacog.config_parser import cfg

memory = Memory(location="./cachedir", verbose=0)

SOURCES_LABEL_AV = dirs.derivatives / "sources_label_av"
SOURCES_PSD_DIR = dirs.derivatives / "sources_epochs"


@memory.cache
def load_source_data():
    X = []
    dfs = []
    for subj in tqdm(cfg.subjects):
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
        "fsaverage", subjects_dir=dirs.fsf_subjects, parc=parc
    )
    src_path = dirs.fsf_subjects / "fsaverage/bem/fsaverage-oct-6-src.fif"
    src = read_source_spaces(src_path)
    os.environ["dirs.fsf_subjects"] = str(dirs.fsf_subjects)
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
