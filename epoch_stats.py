"""Print number of epochs for each subject"""
from collections import OrderedDict

import numpy as np
from mne import read_epochs
import matplotlib.pyplot as plt

# Fixing random state for reproducibility

from config import subjects, bp_epochs


def print_epoch_stats(ep_counts):
    mean_high = 0
    mean_low = 0
    for subj in ep_counts:
        n_high = ep_counts[subj]["high"]
        n_low = ep_counts[subj]["low"]
        mean_high += n_high
        mean_low += n_low
        print(
            "sub-{subj}: high={high}, low={low}".format(
                subj=subj, high=n_high, low=n_low,
            )
        )
    mean_high /= len(ep_counts)
    mean_low /= len(ep_counts)
    print("------------------------")
    print("mean:", f"high={round(mean_high, 1)}", f"low={round(mean_low, 1)}")


def plot_hists(ep_counts, n_bins=10):
    high = np.array([v["high"] for k, v in ep_counts.items()])
    low = np.array([v["low"] for k, v in ep_counts.items()])

    fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

    # We can set the number of bins with the `bins` kwarg
    axs[0].hist(high, bins=n_bins, label="high")
    axs[0].set_title("high",)
    axs[1].hist(low, bins=n_bins, label="low")
    axs[1].set_title("low")
    plt.show()


def read_stats(epoch_type="answer"):
    ep_counts = OrderedDict()
    for subj in subjects:
        ep_path = bp_epochs.fpath(subject=subj)
        ep = read_epochs(str(ep_path), preload=False, verbose="ERROR")

        ep_counts[subj] = dict(
            high=len(ep[f"{epoch_type}/high"]),
            low=len(ep[f"{epoch_type}/low"]),
        )
    return ep_counts


ep_counts = read_stats()
print_epoch_stats(ep_counts)
plot_hists(ep_counts, n_bins=15)
