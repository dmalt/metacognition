"""Mark bad channels and segments for maxfilter"""

from mne.io import read_raw_fif
from mne.chpi import filter_chpi
from mne import read_annotations, set_log_level

from config import BIDS_ROOT, BADS_DIR

set_log_level(verbose="ERROR")


def inspect_fif(f, bads, annotations):
    raw_check = read_raw_fif(str(f), preload=True)
    if bads:
        raw_check.info['bads'] = bads
    if annotations:
        raw_check.set_annotations(annotations)
    bids_dict = dict_from_bids_fname(f.name)
    if bids_dict["sub"] != "emptyroom":
        filter_chpi(raw_check)
    raw_check.plot(block=True, lowpass=50, n_channels=50)
    return raw_check.info['bads'], raw_check.annotations


def write_bads_info_and_annotations(subj, fif_file):
    dest_dir = BADS_DIR / subj.name
    if subj.name == "sub-emptyroom":
        bids_dict = dict_from_bids_fname(fif_file.name)
        dest_dir = dest_dir / ("ses-" + bids_dict["ses"])
    dest_dir.mkdir(exist_ok=True)

    basename = fif_file.name[:-len("_meg.fif")]

    bads_fpath = dest_dir / (basename + "-bads.tsv")
    if bads_fpath.exists():
        with open(bads_fpath, 'r') as f:
            bads = f.readline().split("\t")
            print("Loading BADS from file:", bads)
    else:
        bads = None

    annotations_fpath = dest_dir / (basename + "-annot.fif")
    if annotations_fpath.exists():
        print("Loading annotations from file.")
        annotations = read_annotations(str(annotations_fpath))
    else:
        annotations = None

    bads, annotations = inspect_fif(fif_file, bads, annotations)

    with open(bads_fpath, 'w') as f:
        f.write("\t".join(bads))

    annotations.save(str(annotations_fpath))


if __name__ == "__main__":
    # subjs = BIDS_ROOT.glob("sub-[0-9][1-9]")
    subjs = BIDS_ROOT.glob("sub-*")
    for s in subjs:
        fif_files = s.rglob("*_meg.fif")
        for f in fif_files:
            print(f"Processing {f}")
            write_bads_info_and_annotations(s, f)
