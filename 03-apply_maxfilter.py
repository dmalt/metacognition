"""
Perform Maxwell filtering on annotated data with SSS

Note
----
requires mne >= 0.20 for filtering line noise with filter_chpi
for emptyroom data

"""
import sys

from mne.io import read_raw_fif
from mne.chpi import filter_chpi
from mne import read_annotations
from mne.preprocessing import maxwell_filter
from mne.channels import fix_mag_coil_types


from config import (
    crosstalk_file,
    cal_file,
    maxfilt_config,
    bp_root,
    bp_bads,
    bp_annot,
    bp_maxfilt,
)
from utils import setup_logging
from dataset_specific_utils import parse_args

logger = setup_logging(__file__)


def prepare_raw(raw_path, bads_path, annot_path, is_er):
    """Load raw, filter chpi and line noise, set bads and annotations"""
    raw = read_raw_fif(raw_path, preload=True)
    filter_chpi(
        raw, allow_line_only=is_er, t_window=maxfilt_config["t_window"]
    )
    fix_mag_coil_types(raw.info)

    with open(bads_path, "r") as f:
        bads = f.readline().split("\t")
        if bads == [""]:
            bads = []
        raw.info["bads"] = bads

    raw.set_annotations(read_annotations(annot_path))

    return raw


def apply_maxfilter(raw_path, bads_path, annot_path, maxfilt_path, is_er):
    raw = prepare_raw(raw_path, bads_path, annot_path, is_er)

    coord_frame = "head" if is_er else "meg"

    raw_sss = maxwell_filter(
        raw,
        cross_talk=crosstalk_file,
        calibration=cal_file,
        skip_by_annotation=[],
        coord_frame=coord_frame,
    )

    raw_sss.save(maxfilt_path, overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], emptyroom=True)
    subj, task, run, ses = args.subject, args.task, args.run, args.session

    # input
    raw = bp_root.fpath(subject=subj, task=task, run=run, session=ses)
    bads = bp_bads.fpath(subject=subj, task=task, run=run, session=ses)
    annot = bp_annot.fpath(subject=subj, task=task, run=run, session=ses)
    # output
    maxfilt = bp_maxfilt.fpath(subject=subj, task=task, run=run, session=ses)

    maxfilt.parent.mkdir(exist_ok=True)

    apply_maxfilter(raw, bads, annot, maxfilt, subj == "emptyroom")
