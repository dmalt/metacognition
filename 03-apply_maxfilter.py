"""
Perform Maxwell filtering on annotated data with SSS

Note
----
requires mne >= 0.20 for filtering line noise with filter_chpi
for emptyroom data

"""
import sys

from mne.io import read_raw_fif
from mne.chpi import filter_chpi, read_head_pos
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
    bp_headpos,
    bp_maxfilt,
)
from utils import setup_logging, update_bps, parse_args

logger = setup_logging(__file__)


def prepare_raw_and_hp(src_bp_raw, bads_bp, annot_bp, hp_bp):
    """Load raw, filter chpi and line noise, set bads and annotations"""

    raw = read_raw_fif(str(src_bp_raw), preload=True)
    if bads_bp.subject == "emptyroom":
        filter_chpi(
            raw, allow_line_only=True, t_window=maxfilt_config["t_window"]
        )
    else:
        filter_chpi(
            raw, allow_line_only=False, t_window=maxfilt_config["t_window"]
        )
    fix_mag_coil_types(raw.info)

    with open(bads_bp, "r") as f:
        bads = f.readline().split("\t")
        if bads == [""]:
            bads = []
        raw.info["bads"] = bads

    raw.set_annotations(read_annotations(str(annot_bp)))

    if bads_bp.subject != "emptyroom":
        head_pos = read_head_pos(str(hp_bp))
    else:
        head_pos = None

    return raw, head_pos


def apply_maxfilter(bp_raw, bp_bads, bp_annot, bp_hp, bp_dest):
    raw, head_pos = prepare_raw_and_hp(bp_raw, bp_bads, bp_annot, bp_hp)

    subj_id = bp_dest.subject
    if subj_id == "emptyroom":
        coord_frame = "meg"
    else:
        coord_frame = "head"

    raw_sss = maxwell_filter(
        raw,
        cross_talk=str(crosstalk_file),
        calibration=str(cal_file),
        skip_by_annotation=[],
        coord_frame=coord_frame,
    )

    raw_sss.save(bp_dest.fpath, overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)

    bp_raw, bp_bads, bp_annot, bp_hp, bp_dest = update_bps(
        [bp_root, bp_bads, bp_annot, bp_headpos, bp_maxfilt],
        subject=args.subject,
        task=args.task,
        run=args.run,
        session=args.session,
    )
    bp_dest.mkdir()
    apply_maxfilter(bp_raw, bp_bads, bp_annot, bp_hp, bp_dest)
