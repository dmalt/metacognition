from argparse import ArgumentParser

from mne.io import read_info
from mne import (
    setup_source_space,
    make_bem_solution,
    make_bem_model,
    make_forward_solution,
    write_forward_solution
)

from metacog.config_parser import cfg
from metacog import bp
from metacog.paths import dirs

parser = ArgumentParser(description="compute forward modeel")
parser.add_argument("subject", help="subject id")
subj = parser.parse_args().subject

info_path = bp.root.fpath(subject=subj, task="questions", run=1, session=None)
info = read_info(info_path)

src = setup_source_space(
    f"sub-{subj}",
    spacing=cfg.fwd_config["spacing"],
    add_dist="patch",
    subjects_dir=dirs.fsf_subjects,
)

model = make_bem_model(
    subject=f"sub-{subj}",
    ico=cfg.fwd_config["ico"],
    conductivity=cfg.fwd_config["conductivity"],
    subjects_dir=dirs.fsf_subjects,
)
bem = make_bem_solution(model)
fwd = make_forward_solution(
    info,
    trans=bp.trans.fpath(subject=subj),
    src=src,
    bem=bem,
    meg=True,
    eeg=False,
    mindist=cfg.fwd_config["mindist"],
    n_jobs=8,
    verbose=True,
)

fwd_path = bp.fwd.fpath(subject=subj)
fwd_path.parent.mkdir(exist_ok=True)
write_forward_solution(fwd_path, fwd=fwd, overwrite=True)
