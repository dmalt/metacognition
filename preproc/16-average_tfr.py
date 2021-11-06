"""Compute power time course in target frequency bins"""
from argparse import ArgumentParser
import numpy as np
from mne.time_frequency import read_tfrs

from metacog import bp
from metacog.config_parser import cfg


parser = ArgumentParser(__doc__)
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

tfr_path = bp.tfr.fpath(subject=subj)
tfr = read_tfrs(tfr_path)[0]
fr = tfr.freqs
for band in cfg.target_bands:
    fr_inds = np.logical_and(
        fr >= cfg.target_bands[band][0], fr <= cfg.target_bands[band][1]
    )
    data = tfr.data[:, :, fr_inds, :].mean(axis=2, keepdims=True)
    tfr_band = tfr.copy()
    tfr_band.data = data
    tfr_band.freqs = [cfg.target_bands[band][0]]
    tfr_av_path = bp.tfr_av.fpath(subject=subj, acquisition=band)
    tfr_av_path.parent.mkdir(exist_ok=True, parents=True)
    tfr_band.save(tfr_av_path, overwrite=True)
