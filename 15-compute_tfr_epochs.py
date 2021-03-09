"""Compute averaged time-frequency decomposition and ITC for epochs"""
from argparse import ArgumentParser

import numpy as np
from mne import read_epochs
from mne.time_frequency import tfr_morlet

from config import bp_epochs, bp_tfr, tfr_config
from utils import setup_logging

logger = setup_logging(__file__)

parser = ArgumentParser(__doc__)
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

# input
ep_path = bp_epochs.fpath(subject=subj)
# output
tfr_path = bp_tfr.fpath(subject=subj)
# itc_path_low = bp_itc.fpath(subject=subj, task="low")

# tfr_path_high = bp_tfr.fpath(subject=subj, task="high")
# itc_path_high = bp_itc.fpath(subject=subj, task="high")

ep = read_epochs(ep_path)

freqs = np.arange(**tfr_config["freqs"])
n_cycles = freqs / 2.0
ep_tfr = tfr_morlet(
    ep["answer"],
    average=False,
    return_itc=False,
    freqs=freqs,
    n_cycles=n_cycles,
    decim=tfr_config["decim"],
    use_fft=tfr_config["use_fft"],
)

# ep_tfr_high, ep_itc_high = tfr_morlet(
#     ep["answer/high"],
#     average=True,
#     return_itc=True,
#     freqs=freqs,
#     n_cycles=n_cycles,
#     decim=tfr_config["decim"],
#     use_fft=tfr_config["use_fft"],
# )
tfr_path.parent.mkdir(exist_ok=True, parents=True)
ep_tfr.save(tfr_path, overwrite=True)
# ep_itc_low.save(itc_path_low, overwrite=True)

# ep_tfr_high.save(tfr_path_high, overwrite=True)
# ep_itc_high.save(itc_path_high, overwrite=True)
