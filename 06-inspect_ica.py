"""Manually mark bad ICA components and apply solution"""
import sys

from mne.io import read_raw_fif
from mne.preprocessing import read_ica

from config import bp_ica_sol, bp_filt, bp_ica_bads
from utils import setup_logging, read_ica_bads, write_ica_bads
from dataset_specific_utils import parse_args

logger = setup_logging(__file__)


def inspect_ica(filt_path, ica_sol_path, ica_bads_path):
    raw = read_raw_fif(filt_path, preload=True)
    ica = read_ica(ica_sol_path)
    if ica_bads_path.exists():
        ica.exclude = read_ica_bads(ica_bads_path, logger)
    ica.plot_sources(raw, block=True)
    logger.info(f"Excluding ICs {ica.exclude}")
    write_ica_bads(ica_bads_path, ica, logger)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task = args.subject, args.task

    # input
    filt = bp_filt.fpath(subject=subj, task=task)
    ica_sol = bp_ica_sol.fpath(subject=subj, task=task)
    # output
    ica_bads = bp_ica_bads.fpath(subject=subj, task=task)

    ica_bads.parent.mkdir(exist_ok=True)
    # logger.info(f"Processing {args.path}")
    # print(f"Processing {args.path}")
    inspect_ica(filt, ica_sol, ica_bads)
