"""Manually mark bad channels and segments for maxfilter"""
import sys
from pathlib import Path
from typing import List

from mne.io import read_raw_fif
from mne.chpi import filter_chpi
from mne import read_annotations, Annotations

from utils import setup_logging, bids_from_path, update_bps, parse_args
from config import bp_root, bp_bads, bp_annot

logger = setup_logging(__file__)


def inspect_fif(
    fif_path: Path, bads: List[str], annotations: Annotations
) -> (List[str], Annotations):
    """Manually mark bad channels and segments in gui signal viewer"""
    raw_check = read_raw_fif(str(fif_path), preload=True)
    if bads is not None:
        raw_check.info["bads"] = bads
    if annotations is not None:
        raw_check.set_annotations(annotations)
    bids_fpath = bids_from_path(fif_path)
    if bids_fpath.subject != "emptyroom":
        filter_chpi(raw_check, t_window="auto")
    raw_check.plot(block=True, lowpass=100, highpass=0.5, n_channels=50)
    logger.info(f"Channels marked bad: {raw_check.info['bads']}")
    return raw_check.info["bads"], raw_check.annotations


def annotate_file(bp_src, bp_bads, bp_annot):
    bp_bads.mkdir()
    if bp_bads.fpath.exists():
        with open(bp_bads, "r") as f:
            bads = f.readline().split("\t")
            logger.info(f"Loading BADS from file: {bads}")
    else:
        bads = None
    if bads == [""]:
        bads = []

    if bp_annot.fpath.exists():
        logger.info("Loading annotations from file.")
        annotations = read_annotations(str(bp_annot))
    else:
        annotations = None

    bads, annotations = inspect_fif(bp_src.fpath, bads, annotations)

    with open(bp_bads, "w") as f:
        f.write("\t".join(bads))

    annotations.save(str(bp_annot))


if __name__ == "__main__":

    args = parse_args(
        description=__doc__, args=sys.argv[1:], is_applied_to_er=True
    )

    bp_src, dest_bp_bads, dest_bp_annot = update_bps(
        [bp_root, bp_bads, bp_annot],
        subject=args.subject,
        task=args.task,
        run=args.run,
        session=args.session,
    )

    annotate_file(bp_src, dest_bp_bads, dest_bp_annot)
