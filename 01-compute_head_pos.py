"""
Compute head postion for each file to make decision on movement compensation.

Note
----
This script utilized new features added to MNE-python v.0.20.
At the moment MNE v.0.20 is in development and latest MNE-BIDS isn't
compatible with it.

"""
from mne.chpi import (
    compute_chpi_amplitudes,
    compute_chpi_locs,
    compute_head_pos,
    write_head_pos,
)
from mne.io import read_raw_fif
import mne

from config import BIDS_ROOT, HP_DIR
from utils import BidsFname
from utils import output_log

output_log(__file__)

def compute_head_position(f):
    raw = read_raw_fif(str(f))
    chpi_ampl = compute_chpi_amplitudes(raw)
    chpi_locs = compute_chpi_locs(raw.info, chpi_ampl)
    return compute_head_pos(raw.info, chpi_locs)


def compute_and_save_hp(fif_file, dest):
    head_pos = compute_head_position(fif_file)
    bids_fname = BidsFname(fif_file.name)
    if "part" in bids_fname:
        bids_fname["part"] = None
    base_path = str(dest / bids_fname.base)
    write_head_pos(base_path + "_hp.pos", head_pos)


if __name__ == "__main__":
    subjs = list(BIDS_ROOT.glob("sub-[0-9][1-9]"))
    for subj in subjs:
        # create destination folder
        dest_dir = HP_DIR / subj.name
        dest_dir.mkdir(exist_ok=True)

        fif_files = filter(
            lambda s: not s.match("*part-02*"), subj.rglob("*_meg.fif"),
        )
        for f in fif_files:
            print(f"Processing {f}")
            compute_and_save_hp(f, dest_dir)
