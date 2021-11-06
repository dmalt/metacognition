"""
Average source-space single trials over atlas labels

"""

from config import DERIVATIVES_DIR, SUBJECTS_DIR
from argparse import ArgumentParser
from mne import (
    read_labels_from_annot,
    read_source_estimate,
    extract_label_time_course,
    read_source_spaces,
)
import numpy as np

parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject
# subj = "01"


SOURCES_PSD_DIR = DERIVATIVES_DIR / "sources_epochs"
subj_dir = SOURCES_PSD_DIR / f"sub-{subj}"

parc = "aparc.a2009s"
labels = read_labels_from_annot(
    "fsaverage", subjects_dir=SUBJECTS_DIR, parc=parc
)

X = []
for trial_path in sorted(subj_dir.glob("*-rh.stc")):
    X.append(
        read_source_estimate(
            str(trial_path)[: -len("-rh.stc")], subject=f"sub-{subj}"
        )
    )

src_path = SUBJECTS_DIR / "fsaverage/bem/fsaverage-oct-6-src.fif"
src = read_source_spaces(src_path)
label_ts = extract_label_time_course(X, labels, src)

SOURCES_LABEL_AV = DERIVATIVES_DIR / "sources_label_av"
subj_dir = SOURCES_LABEL_AV / f"sub-{subj}"
subj_dir.mkdir(exist_ok=True, parents=True)
for i, trial in enumerate(label_ts):
    np.save(subj_dir / f"sub-{subj}_parc-{parc}_trial-{i:03d}", trial)
