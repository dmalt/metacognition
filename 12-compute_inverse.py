from argparse import ArgumentParser

from mne import compute_raw_covariance, read_info
from mne.io import read_raw_fif
from mne.minimum_norm import make_inverse_operator

from config import bp_root, fwd_path, bp_epochs

parser = ArgumentParser(description="Compute sources")
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

bp_er = bp_root.copy().update(subject=subj, task="rest").find_empty_room()
er_raw = read_raw_fif(bp_er.fpath)
noise_cov = compute_raw_covariance(er_raw, method="auto")

bp_epochs = bp_epochs.update(subject=subj, task="questions")
info = read_info(bp_epochs.fpath)

fwd_path.format(subject=subj)

inverse_operator = make_inverse_operator(epochs.info, fwd, common_cov)
