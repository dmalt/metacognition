"""
Apply tsss + movement compensation + head position translation

Note
----
requires mne >= 0.20 for filtering line noise with filter_chpi
for emptyroom data

"""

from mne.io import read_raw_fif
from mne.chpi import filter_chpi, read_head_pos
from mne import read_annotations
from mne.preprocessing import maxwell_filter
from mne.channels import fix_mag_coil_types

from config import (
    BIDS_ROOT,
    HP_DIR,
    BADS_DIR,
    MAXFILTER_DIR,
    crosstalk_file,
    cal_file,
)
from utils import output_log, BidsFname

output_log(__file__)


def prepare_raw_and_hp(fif_file):
    """Load raw, filter chpi and line noise, set bads and annotations"""
    bids_fname = BidsFname(fif_file.name)
    subj_name = bids_fname.to_string("sub")

    raw = read_raw_fif(str(fif_file), preload=True)
    if subj_name == "sub-emptyroom":
        filter_chpi(raw, allow_line_only=True, t_window="auto")
    else:
        filter_chpi(raw, allow_line_only=False, t_window="auto")
    fix_mag_coil_types(raw.info)

    bads_dir = BADS_DIR / subj_name
    if subj_name == "sub-emptyroom":
        session_name = bids_fname.to_string("ses")
        bads_dir = bads_dir / session_name
    if "part" in bids_fname:
        bids_fname["part"] = None

    bads_path = bads_dir / (bids_fname.base + "-bads.tsv")
    with open(bads_path, "r") as f:
        raw.info["bads"] = f.readline().split("\t")

    annot_path = bads_dir / (bids_fname.base + "-annot.fif")
    raw.set_annotations(read_annotations(str(annot_path)))

    if subj_name != "sub-emptyroom":
        head_pos_path = next((HP_DIR / subj_name).glob(f"{subj_name}*_hp.pos"))
        head_pos = read_head_pos(str(head_pos_path))
    else:
        head_pos = None

    return raw, head_pos


def apply_maxfilter(fif_file, subj):
    raw, head_pos = prepare_raw_and_hp(fif_file)

    if subj.name == "sub-emptyroom":
        coord_frame = "meg"
        # destination = None
    else:
        coord_frame = "head"
        # destination = (0, 0, 0.04)

    raw_sss = maxwell_filter(
        raw,
        cross_talk=str(crosstalk_file),
        calibration=str(cal_file),
        # st_duration=20,
        # head_pos=head_pos,
        # destination=destination,
        skip_by_annotation=[],
        coord_frame=coord_frame,
    )

    dest_dir = MAXFILTER_DIR / subj.name
    dest_dir.mkdir(exist_ok=True)
    bids_fname = BidsFname(fif_file.name)
    if "part" in bids_fname:
        bids_fname["part"] = None
    bids_fname["proc"] = "sss"
    savepath = str(dest_dir / str(bids_fname))
    raw_sss.save(savepath, overwrite=True)


if __name__ == "__main__":
    subjs = BIDS_ROOT.glob("sub-*")
    # subjs = BIDS_ROOT.glob("sub-06")
    for subj in subjs:
        fif_files = filter(
            lambda s: not s.match("*part-02*"), subj.rglob("*_meg.fif"),
        )
        for f in fif_files:
            print(f"Processing {f.name}")
            apply_maxfilter(f, subj)
