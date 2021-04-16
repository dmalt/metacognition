"""
Compute head postion for each file

"""
import sys
from pathlib import Path

import numpy as np
from mne.chpi import (
    compute_chpi_amplitudes,
    compute_chpi_locs,
    compute_head_pos,
    write_head_pos,
)
from mne.io import read_raw_fif

from metacog.paths import bp_root, bp_headpos
from metacog.utils import setup_logging
from metacog.dataset_specific_utils import parse_args

logger = setup_logging(__file__)


def compute_head_position(src: Path) -> np.ndarray:
    raw = read_raw_fif(src)
    chpi_ampl = compute_chpi_amplitudes(raw)
    chpi_locs = compute_chpi_locs(raw.info, chpi_ampl)
    return compute_head_pos(raw.info, chpi_locs)


if __name__ == "__main__":
    args = parse_args(description=__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task, run = args.subject, args.task, args.run

    # input
    raw = bp_root.fpath(subject=subj, task=task, run=run, session=None)
    # output
    headpos = bp_headpos.fpath(subject=subj, task=task, run=run)

    headpos.parent.mkdir(exist_ok=True)
    logger.info(f"Processing {raw.name} --> {headpos}")

    head_pos = compute_head_position(raw)
    write_head_pos(headpos, head_pos)
