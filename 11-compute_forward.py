from argparse import ArgumentParser

import mne

from config import (
    SUBJECTS_DIR,
    FORWARDS_DIR,
    bp_root,
    fwd_config,
    trans_path
)


parser = ArgumentParser(description="compute forward modeel")
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

trans_path = trans_path.format(subject=subj)

bp_info_src = bp_root.copy().update(
    subject=args.subject, task="questions", run=1
)

info = mne.io.read_info(bp_info_src.fpath)

src = mne.setup_source_space(
    f"sub-{subj}",
    spacing=fwd_config["spacing"],
    add_dist="patch",
    subjects_dir=SUBJECTS_DIR,
)


model = mne.make_bem_model(
    subject=f"sub-{subj}",
    ico=fwd_config["ico"],
    conductivity=fwd_config["conductivity"],
    subjects_dir=SUBJECTS_DIR,
)
bem = mne.make_bem_solution(model)
fwd = mne.make_forward_solution(
    info,
    trans=trans_path,
    src=src,
    bem=bem,
    meg=True,
    eeg=False,
    mindist=fwd_config["mindist"],
    n_jobs=8,
    verbose=True,
)

mne.write_forward_solution(
    str(
        FORWARDS_DIR / f"sub-{subj}_spacing-{fwd_config['spacing']}-fwd.fif"
    ),
    fwd=fwd,
    overwrite=True,
)
