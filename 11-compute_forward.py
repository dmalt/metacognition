from argparse import ArgumentParser

from mne.io import read_info
from mne import (
    setup_source_space,
    make_bem_solution,
    make_bem_model,
    make_forward_solution,
    write_forward_solution
)

from config import SUBJECTS_DIR, bp_root, fwd_config, bp_trans, bp_fwd

parser = ArgumentParser(description="compute forward modeel")
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

info_path = bp_root.fpath(subject=subj, task="questions", run=1, session=None)
info = read_info(info_path)

src = setup_source_space(
    f"sub-{subj}",
    spacing=fwd_config["spacing"],
    add_dist="patch",
    subjects_dir=SUBJECTS_DIR,
)

model = make_bem_model(
    subject=f"sub-{subj}",
    ico=fwd_config["ico"],
    conductivity=fwd_config["conductivity"],
    subjects_dir=SUBJECTS_DIR,
)
bem = make_bem_solution(model)
fwd = make_forward_solution(
    info,
    trans=bp_trans.fpath(subject=subj),
    src=src,
    bem=bem,
    meg=True,
    eeg=False,
    mindist=fwd_config["mindist"],
    n_jobs=8,
    verbose=True,
)

fwd_path = bp_fwd.fpath(subject=subj)
fwd_path.parent.mkdir(exist_ok=True)
write_forward_solution(fwd_path, fwd=fwd, overwrite=True)
