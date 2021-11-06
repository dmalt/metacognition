from __future__ import annotations


# ----------------------- set these in config_user.py ----------------------- #
BIDS_ROOT: str      # path to BIDS root folder (the one with subjects` data)

DATASET_NAME: str   # name of the dataset
AUTHORS: list[str]  # list of dataset authors

tasks: list[str]
subj_tasks: dict[str, list[str]]

all_subjects: list[str]
bad_subjects: list[str]
subjects: list[str]

runs: list[str]
subj_runs: dict[str, list[str]]

er_sessions: list[str]
# --------------------------------------------------------------------------- #


# ---------------------------- 03-apply_maxfilter --------------------------- #
maxfilt_config: dict = {"t_window": "auto"}
# --------------------------------------------------------------------------- #

# -------- 04-concat_filter_resample -------- #
concat_config: dict = {
    "filter_freqs": (1, 100), "resamp_freq": 500, "pad": "symmetric",
}
# ------------------------------------------- #

# -------- 05-compute_ica -------- #
ica_config: dict = {
    "random_state": 28,
    "n_components": 0.99,
    "decim": 5,
    "annot_rej": True,
    "max_iter": 1000,
}
# -------------------------------- #

# -------- 09-make_epochs -------- #
epochs_config: dict = dict(
    tmin=-1,
    tmax=1,
    baseline=None,
    reject=None,
    flat=None,
    reject_by_annotation=True,
    on_missing="ignore",
)
EVENTS_ID: dict[str, int] = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidence": 5,
}
# -------------------------------- #

# -------- FSF -------- #
fsf_config: dict = {"openmp": 8}
# --------------------- #

# -------- 11-compute_forward -------- #
fwd_config: dict = {
    "mindist": 5.0,
    "ico": 4,
    "conductivity": (0.3,),
    "spacing": "oct6",
}
# ------------------------------------ #

# -------- 13-compute_sources -------- #
config_sources: dict = dict(
    baseline_win=[-1, -0.25],
    active_win=[0.25, 1],
)
# ------------------------------------ #

# -------- 15-compute_tfr_epochs -------- #
tfr_config: dict = dict(
    freqs=dict(start=1.0, stop=30., step=1.),
    decim=4,
    use_fft=True,
)
# -------------------------------------- #

# ----------- 16-average_tfr ----------- #
target_bands: dict[str, tuple[float, float]] = {
    "alpha": (8., 12.),
    "delta": (2., 4.),
    "theta": (4., 8.),
    "beta": (13., 25.),
}
# -------------------------------------- #
