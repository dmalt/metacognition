"""Annotate bad segments for epochs creation"""
import sys

from mne import read_annotations
from mne.io import read_raw_fif

from utils import setup_logging, update_bps, parse_args
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


def annotate_file(fif_file, bp_annot):
    if bp_annot.fpath.exists():
        logger.info("Loading annotations from file.")
        annotations = read_annotations(str(bp_annot))
    else:
        annotations = None
    annotations = inspect_fif(fif_file, annotations)
    annotations.save(str(bp_annot.fpath))


if __name__ == "__main__":
    args = parse_args(
        description=__doc__, args=sys.argv[1:], is_applied_to_er=True
    )

    bp_src, dest_bp_annot = update_bps(
        [bp_ica, bp_annot_final],
        subject=args.subject,
        task=args.task,
        session=args.session,
    )
    dest_bp_annot.mkdir(exist_ok=True)

    annotate_file(bp_src.fpath, dest_bp_annot)
