"""
Cluster-based permutation test for correlations
"""


def compte_stat():
    """
    Compute cluster-level statistic
    """
    pass


def spatio_temporal_cluster_correlation_test(adjacency, n_permutatons=1024):
    """
    TODO
    """
    # 1. Compute real stats for each data point
    #   - use t-value for correlation coefficients
    # 2. Find clusters
    #   - threshold t-values
    #   - find clusters using adjacency matrix
    # 3. For each cluster compute cluster-level statistic
    # 4. Do permutations
    #   - leave data in place, permute trials behav data between trials within
    #     each subject
    #   - on each permutation compute point-wise stats, find clusters,
    #     compute stats for each and find maximum-stat cluster
    #   - store max-stats from each permutation; compute hist at the end
    pass


# _find_clusters(x, threshold, tail=0, adjacency=None, max_step=1, include=None, partitions=None, t_power=1, show_info=False):

if __name__ == "__main__":
    from tf_analysis import load_data, make_cumulative_df
    from mne.channels import find_ch_adjacency
    from mne.io import read_info

    from config import bp_epochs

    time_ind = 100
    ch_ind = 1
    band = "alpha"
    dfs, data = load_data(band)
    cumulative_df = make_cumulative_df(dfs, data, ch_ind, time_ind)

    info_src = bp_epochs.fpath(subject="01")
    info = read_info(info_src)
    adjacency, ch_names = find_ch_adjacency(info, ch_type="grad")
