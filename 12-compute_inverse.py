"""Compute inverse solution"""
from argparse import ArgumentParser
import json

from mne import compute_raw_covariance, read_forward_solution
from mne.preprocessing import read_ica
from mne.io import read_raw_fif, read_info
from mne.minimum_norm import make_inverse_operator, write_inverse_operator

from config import (
    bp_fwd,
    bp_epochs,
    bp_inv,
    bp_root_json,
    dirs,
    bp_ica_sol,
    bp_ica_bads,
)
from utils import setup_logging, read_ica_bads

logger = setup_logging(__file__)

parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

json_path = bp_root_json.fpath(subject=subj, task="rest", run=None)
with open(json_path, "r") as f:
    er_relpath = json.load(f)["AssociatedEmptyRoom"]
er_path = dirs.bids_root / er_relpath

er_raw = read_raw_fif(er_path, preload=True)

# remove ICA components marked for 'quesitions' data from ER data
ica_sol_path = bp_ica_sol.fpath(subject=subj, task="questions")
ica_bads_path = bp_ica_bads.fpath(subject=subj, task="questions")
ica = read_ica(ica_sol_path)
ica.exclude = read_ica_bads(ica_bads_path, logger)
logger.info(f"Excluding ICs {ica.exclude} from ER data")
ica.apply(er_raw)

noise_cov = compute_raw_covariance(er_raw, method="auto")
del er_raw

info = read_info(bp_epochs.fpath(subject=subj))

fwd = read_forward_solution(bp_fwd.fpath(subject=subj))

inv_path = bp_inv.fpath(subject=subj)
inverse_operator = make_inverse_operator(info, fwd, noise_cov, rank="info")
write_inverse_operator(inv_path, inverse_operator)
