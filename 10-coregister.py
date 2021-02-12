"""MRI <--> head coordinates coregistration"""
from argparse import ArgumentParser
import os

from mne.gui import coregistration

from config import SUBJECTS_DIR, bp_root, trans_path

parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

info_src = bp_root.update(subject=subj, task="questions", run=1).fpath

trans_path = trans_path.format(subject=subj)
trans_path = trans_path if os.path.exists(trans_path) else None

coregistration(
    subject=f"sub-{subj}",
    subjects_dir=SUBJECTS_DIR,
    inst=info_src,
    trans=trans_path,
)
