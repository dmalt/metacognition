"""Compute power time course in target frequency bins"""
from argparse import ArgumentParser
import numpy as np
from mne.time_frequency import read_tfrs
from config import target_bands, bp_tfr, bp_tfr_av


parser = ArgumentParser(__doc__)
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

tfr_path = bp_tfr.fpath(subject=subj)
tfr = read_tfrs(tfr_path)[0]
fr = tfr.freqs
for bandname in target_bands:
    fr_inds = np.logical_and(
        fr >= target_bands[bandname][0], fr <= target_bands[bandname][1]
    )
    data = tfr.data[:, :, fr_inds, :].mean(axis=2, keepdims=True)
    tfr_band = tfr.copy()
    tfr_band.data = data
    tfr_band.freqs = [target_bands[bandname][0]]
    tfr_av_path = bp_tfr_av.fpath(subject=subj, acquisition=bandname)
    tfr_av_path.parent.mkdir(exist_ok=True, parents=True)
    tfr_band.save(tfr_av_path, overwrite=True)
