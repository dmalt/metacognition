"""Compute sources from epochs"""
from argparse import ArgumentParser

from mne import (
    read_epochs,
    read_forward_solution,
    compute_source_morph,
    read_source_spaces,
)

from mne.minimum_norm import (
    compute_source_psd_epochs,
    apply_inverse_epochs,
    read_inverse_operator,
)


from metacog.paths import dirs
from metacog import bp
from metacog.utils import setup_logging

logger = setup_logging(__file__)
SOURCES_PSD_DIR = dirs.derivatives / "sources_epochs"


parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

fwd_path = bp.fwd.fpath(subject=subj)
fwd = read_forward_solution(fwd_path)
inv_path = bp.inv.fpath(subject=subj)

epochs_path = bp.epochs.fpath(subject=subj)
epochs = read_epochs(epochs_path)["answer"]
inverse_operator = read_inverse_operator(inv_path)

epochs.apply_baseline()

stcs = apply_inverse_epochs(
    epochs, inverse_operator, lambda2=1, method="MNE"
)


src_path = dirs.fsf_subjects / "fsaverage/bem/fsaverage-oct-6-src.fif"
src = read_source_spaces(src_path)
fsave_vertices = [s["vertno"] for s in src]

morph = compute_source_morph(
    src=inverse_operator["src"],
    subject_to="fsaverage",
    spacing=fsave_vertices,
    subjects_dir=dirs.fsf_subjects,
)
subj_dir = SOURCES_PSD_DIR / f"sub-{subj}"
subj_dir.mkdir(exist_ok=True, parents=True)

for i, s in enumerate(stcs):
    morph.apply(s).save(subj_dir / f"sub-{subj}_trial-{i:03d}")
epochs.metadata.to_pickle(subj_dir / f"sub-{subj}_df.pkl")
