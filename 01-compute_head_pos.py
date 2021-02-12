"""
Compute head postion for each file

"""
import sys

import numpy as np
from mne.chpi import (
    compute_chpi_amplitudes,
    compute_chpi_locs,
    compute_head_pos,
    write_head_pos,
)
from mne.io import read_raw_fif
from mne_bids import BIDSPath

from config import bp_root, bp_headpos
from utils import setup_logging, update_bps, parse_args

logger = setup_logging(__file__)


def compute_head_position(src_bp: BIDSPath) -> np.ndarray:
    raw = read_raw_fif(src_bp.fpath)
    chpi_ampl = compute_chpi_amplitudes(raw)
    chpi_locs = compute_chpi_locs(raw.info, chpi_ampl)
    return compute_head_pos(raw.info, chpi_locs)


if __name__ == "__main__":
    args = parse_args(
        description=__doc__, args=sys.argv[1:], is_applied_to_er=False
    )
    src_bp, dest_bp = update_bps(
        [bp_root, bp_headpos],
        subject=args.subject,
        task=args.task,
        run=args.run,
    )
    dest_bp.mkdir()
    logger.info(
        f"Processing {src_bp.basename} --> {dest_bp.fpath}"
    )

    head_pos = compute_head_position(src_bp)
    write_head_pos(dest_bp.fpath, head_pos)
