"""Annotate bad segments for epochs creation"""
import sys

from mne import read_annotations
from mne.io import read_raw_fif

from utils import setup_logging
from dataset_specific_utils import parse_args
from config import bp_ica, bp_annot_final

logger = setup_logging(__file__)


def inspect_fif(fif_path, annotations):
    """Manually mark bad channels and segments in gui signal viewer"""
    raw_check = read_raw_fif(fif_path, preload=True)
    if annotations is not None:
        raw_check.set_annotations(annotations)
    raw_check.pick_types(meg="mag")
    raw_check.plot(block=True, lowpass=100, n_channels=102)
    return raw_check.annotations


def annotate_file(fif_file, annot_path):
    if annot_path.exists():
        logger.info("Loading annotations from file.")
        annotations = read_annotations(annot_path)
    else:
        annotations = None
    annotations = inspect_fif(fif_file, annotations)
    annotations.save(annot_path)


if __name__ == "__main__":
    args = parse_args(description=__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task = args.subject, args.task

    # input
    cleaned_fif = bp_ica.fpath(subject=subj, task=task)
    # output
    annot = bp_annot_final.fpath(subject=subj, task=task)

    annot.parent.mkdir(exist_ok=True)

    annotate_file(cleaned_fif, annot)
