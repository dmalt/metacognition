"""Compute sources from epochs"""
from argparse import ArgumentParser

from mne import (
    read_epochs,
    read_forward_solution,
    compute_source_morph,
    read_source_spaces,
)
from mne.minimum_norm import (
    # source_band_induced_power,
    compute_source_psd_epochs,
    read_inverse_operator,
)

from config import (
    SUBJECTS_DIR,
    config_sources,
    SOURCES_DIR,
    bp_fwd,
    bp_epochs,
    bp_inv,
)
from utils import setup_logging

logger = setup_logging(__file__)


parser = ArgumentParser(description=__doc__)
parser.add_argument("subject", help="subject id")
args = parser.parse_args()
subj = args.subject

fwd_path = bp_fwd.fpath(subject=subj)
fwd = read_forward_solution(fwd_path)
inv_path = bp_inv.fpath(subject=subj)

epochs_path = bp_epochs.fpath(subject=subj)
epochs = read_epochs(epochs_path)["answer"]
inverse_operator = read_inverse_operator(inv_path)

# stcs_low = source_band_induced_power(
#     epochs["low"],
#     inverse_operator,
#     bands,
#     n_cycles=2,
#     use_fft=False,
#     n_jobs=4,
#     decim=2,
#     baseline=(-1, 0),
# )

epochs_active = epochs.copy().crop(
    tmin=config_sources["active_win"][0], tmax=config_sources["active_win"][1]
)
epochs_base = epochs.copy().crop(
    tmin=config_sources["baseline_win"][0],
    tmax=config_sources["baseline_win"][1],
)

stcs_low_act = compute_source_psd_epochs(
    epochs_active["low"], inverse_operator, fmin=2, fmax=30, lambda2=2
)

stcs_high_act = compute_source_psd_epochs(
    epochs_active["high"], inverse_operator, fmin=2, fmax=30, lambda2=2
)

stcs_low_base = compute_source_psd_epochs(
    epochs_base["low"], inverse_operator, fmin=2, fmax=30, lambda2=2
)

stcs_high_base = compute_source_psd_epochs(
    epochs_base["high"], inverse_operator, fmin=2, fmax=30, lambda2=2
)

src_path = SUBJECTS_DIR / "fsaverage/bem/fsaverage-oct-6-src.fif"
src = read_source_spaces(src_path)
fsave_vertices = [s["vertno"] for s in src]

morph = compute_source_morph(
    src=inverse_operator["src"],
    subject_to="fsaverage",
    spacing=fsave_vertices,
    subjects_dir=SUBJECTS_DIR,
)
subj_dir = SOURCES_DIR / f"sub-{subj}"
subj_dir.mkdir(exist_ok=True)

for i, s in enumerate(stcs_high_act):
    s /= stcs_high_base[i]
    morph.apply(s).save(subj_dir / f"sub-{subj}_cond-high_trial-{i}")
for i, s in enumerate(stcs_low_act):
    s /= stcs_low_base[i]
    morph.apply(s).save(subj_dir / f"sub-{subj}_cond-low_trial-{i}")

# (sum(stcs_high_base) / len(stcs_high_base) / sum(stcs_low_base) * len(stcs_low_base)).plot(subjects_dir=SUBJECTS_DIR, hemi="both")
