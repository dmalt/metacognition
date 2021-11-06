"""Annotate bad segments for epochs creation"""
import sys

from mne import read_annotations
from mne.io import read_raw_fif

from metacog import bp
from metacog.utils import setup_logging
from metacog.dataset_specific_utils import parse_args

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
    annotations.save(str(annot_path))  # str conversion required


if __name__ == "__main__":
    args = parse_args(description=__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task = args.subject, args.task

    # input
    cleaned_fif = bp.ica.fpath(subject=subj, task=task)
    # output
    annot = bp.annot_final.fpath(subject=subj, task=task)

    annot.parent.mkdir(exist_ok=True, parents=True)

    annotate_file(cleaned_fif, annot)
