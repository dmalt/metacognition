"""MRI <--> head coordinates coregistration"""
from argparse import ArgumentParser

from mne.gui import coregistration

from metacog import bp
from metacog.paths import dirs

parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

info_src = bp.root.fpath(subject=subj, task="questions", run=1, session=None)

trans_path = bp.trans.fpath(subject=subj)
trans_path.parent.mkdir(exist_ok=True)
trans_path = trans_path if trans_path.exists() else None


coregistration(
    subject=f"sub-{subj}",
    subjects_dir=dirs.subjects,
    inst=info_src,
    trans=trans_path,
)
