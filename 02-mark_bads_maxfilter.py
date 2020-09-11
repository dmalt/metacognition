"""Manually mark bad channels and segments for maxfilter"""

from mne.io import read_raw_fif
from mne.chpi import filter_chpi
from mne import read_annotations

from utils import BidsFname
from utils import setup_logging
from config import BIDS_ROOT, BADS_DIR

logger = setup_logging(__file__)


def inspect_fif(f, bads, annotations):
    raw_check = read_raw_fif(str(f), preload=True)
    if bads:
        raw_check.info["bads"] = bads
    if annotations:
        raw_check.set_annotations(annotations)
    bids_fname = BidsFname(f.name)
    if bids_fname["sub"] != "emptyroom":
        filter_chpi(raw_check, t_window="auto")
    raw_check.plot(block=True, lowpass=100, n_channels=50)
    logger.info(f"Channels marked bad: {raw_check.info['bads']}")
    return raw_check.info["bads"], raw_check.annotations


def write_bads_info_and_annotations(subj, fif_file):
    dest_dir = BADS_DIR / subj.name
    bids_fname = BidsFname(fif_file.name)
    if subj.name == "sub-emptyroom":
        dest_dir = dest_dir / bids_fname.to_string("ses")
    dest_dir.mkdir(exist_ok=True)
    if "part" in bids_fname:
        bids_fname["part"] = None

    bads_fpath = dest_dir / (bids_fname.base + "-bads.tsv")
    if bads_fpath.exists():
        with open(bads_fpath, "r") as f:
            bads = f.readline().split("\t")
            logger.info("Loading BADS from file:", bads)
    else:
        bads = None

    annotations_fpath = dest_dir / (bids_fname.base + "-annot.fif")
    if annotations_fpath.exists():
        logger.info("Loading annotations from file.")
        annotations = read_annotations(str(annotations_fpath))
    else:
        annotations = None

    bads, annotations = inspect_fif(fif_file, bads, annotations)

    with open(bads_fpath, "w") as f:
        f.write("\t".join(bads))

    annotations.save(str(annotations_fpath))


if __name__ == "__main__":
    # subjs = BIDS_ROOT.glob("sub-*")
    subjs = BIDS_ROOT.glob("sub-06")
    for subj in subjs:
        fif_files = filter(
            lambda s: not s.match("*part-02*"), subj.rglob("*_meg.fif"),
        )
        for f in fif_files:
            logger.info(f"Processing {f}")
            write_bads_info_and_annotations(subj, f)
