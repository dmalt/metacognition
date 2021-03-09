"""Manually mark bad channels and segments for maxfilter"""
import sys

from mne.io import read_raw_fif
from mne.chpi import filter_chpi
from mne import read_annotations

from utils import setup_logging
from dataset_specific_utils import parse_args
from config import bp_root, bp_bads, bp_annot

logger = setup_logging(__file__)


def inspect_fif(fif_path, bads, annotations, is_emptyroom):
    """Manually mark bad channels and segments in gui signal viewer

    Filter chpi and line noise from data copy for inspection

    """
    raw_check = read_raw_fif(fif_path, preload=True)
    if bads is not None:
        raw_check.info["bads"] = bads
    if annotations is not None:
        raw_check.set_annotations(annotations)
    filter_chpi(raw_check, allow_line_only=is_emptyroom)
    raw_check.plot(block=True, lowpass=100, highpass=0.5, n_channels=50)
    logger.info(f"Channels marked bad: {raw_check.info['bads']}")
    return raw_check.info["bads"], raw_check.annotations


def read_bads(bads_path):
    with open(bads_path, "r") as f:
        bads = f.readline().split("\t")
        logger.info(f"Loading BADS from file: {bads}")
    if bads == [""]:
        bads = []
    return bads


def write_bads(bads_path, bads):
    with open(bads_path, "w") as f:
        f.write("\t".join(bads))


def annotate_fif(raw_path, bads_path, annot_path, is_emptyroom):
    bads = read_bads(bads_path) if bads_path.exists() else None
    annotations = read_annotations(annot_path) if annot_path.exists() else None

    bads, annotations = inspect_fif(raw_path, bads, annotations, is_emptyroom)

    write_bads(bads_path, bads)
    annotations.save(annot_path)


if __name__ == "__main__":
    args = parse_args(description=__doc__, args=sys.argv[1:], emptyroom=True)
    subj, task, run, ses = args.subject, args.task, args.run, args.session

    # input
    raw = bp_root.fpath(subject=subj, task=task, run=run, session=ses)
    # output
    bads = bp_bads.fpath(subject=subj, task=task, run=run, session=ses)
    annot = bp_annot.fpath(subject=subj, task=task, run=run, session=ses)

    bads.parent.mkdir(exist_ok=True)

    annotate_fif(raw, bads, annot, subj == "emptyroom")
