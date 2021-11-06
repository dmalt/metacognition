"""Add calibration and crosstalk files to data repository"""
from tqdm import tqdm
from mne_bids import write_meg_calibration, write_meg_crosstalk, BIDSPath
from metacog.config_parser import cfg
from metacog.paths import crosstalk, calibration, dirs


sss_data = BIDSPath(root=dirs.bids_root)
for subj in tqdm(cfg.all_subjects):
    sss_data.update(subject=subj)
    write_meg_calibration(calibration, sss_data)
    write_meg_crosstalk(crosstalk, sss_data)
