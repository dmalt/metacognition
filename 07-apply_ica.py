"""Apply ICA solution with marked bad components to raw data"""
import sys

from mne.io import read_raw_fif
from mne.preprocessing import read_ica

from config import bp_ica_sol, bp_filt, bp_ica, bp_ica_bads
from utils import setup_logging, read_ica_bads
from dataset_specific_utils import parse_args

logger = setup_logging(__file__)


def clean_fif(fif_path, ica_sol_path, ica_bads_path, cleaned_fif_path):
    raw = read_raw_fif(fif_path, preload=True)
    ica = read_ica(ica_sol_path)
    ica.exclude = read_ica_bads(ica_bads_path, logger)
    logger.info(f"Excluding ICs {ica.exclude}")
    ica.apply(raw)
    raw.save(cleaned_fif_path, overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task = args.subject, args.task

    # input
    filt = bp_filt.fpath(subject=subj, task=task, session=None)
    ica_sol = bp_ica_sol.fpath(subject=subj, task=task)
    ica_bads = bp_ica_bads.fpath(subject=subj, task=task)
    # output
    cleaned_fif = bp_ica.fpath(subject=subj, task=task)

    cleaned_fif.parent.mkdir(exist_ok=True)
    # logger.info(f"Processing {args.path}")
    # print(f"Processing {args.path}")
    clean_fif(filt, ica_sol, ica_bads, cleaned_fif)
