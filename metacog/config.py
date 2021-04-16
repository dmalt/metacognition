from collections import defaultdict


BIDS_ROOT = "/home/dmalt/Data/metacog_social/"

DATASET_NAME = ("metacognition",)
AUTHORS = (
    [
        "Beatriz Martin Luengo",
        "Maria Alekseeva",
        "Dmitrii Altukhov",
        "Yuri Shtyrov",
    ],
)

target_bands = {
    "alpha": (8, 12),
    "delta": (2, 4),
    "theta": (4, 8),
    "beta": (13, 25),
}

tasks = ["go", "CE", "OE"]
subj_tasks = defaultdict(lambda: tasks)

all_subjects = [
    "01",
]

bad_subjects = ["02", "20", "07"]
subjects = [s for s in all_subjects if s not in bad_subjects]


runs = ["01", "02", "03"]
subj_runs = defaultdict(lambda: runs)
subj_runs["01"] = ["01"]  # first subj has everything in one file

er_sessions = []

# ---------------------------- 03-apply_maxfilter --------------------------- #
maxfilt_config = {"t_window": "auto"}
# --------------------------------------------------------------------------- #

# -------- 04-concat_filter_resample -------- #
concat_config = {
    "filter_freqs": (1, 100), "resamp_freq": 500, "pad": "symmetric",
}
# ------------------------------------------- #

# -------- 05-compute_ica -------- #
ica_config = {
    "random_state": 28,
    "n_components": 0.99,
    "decim": 5,
    "annot_rej": True,
    "max_iter": 1000,
}
# -------------------------------- #

# -------- 09-make_epochs -------- #
epochs_config = dict(
    tmin=-1,
    tmax=1,
    baseline=None,
    reject=None,
    flat=None,
    reject_by_annotation=True,
    on_missing="ignore",
)
EVENTS_ID = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidence": 5,
}
# -------------------------------- #

# -------- FSF -------- #
fsf_config = {"openmp": 8}
# --------------------- #

# -------- 11-compute_forward -------- #
fwd_config = {
    "mindist": 5.0,
    "ico": 4,
    "conductivity": (0.3,),
    "spacing": "oct6",
}
# ------------------------------------ #

# -------- 13-compute_sources -------- #
config_sources = dict(
    baseline_win=[-1, -0.25],
    active_win=[0.25, 1],
)
# ------------------------------------ #

# -------- 15-compute_tfr_epochs -------- #
tfr_config = dict(
    freqs=dict(start=1.0, stop=30., step=1.),
    decim=4,
    use_fft=True,
)
# -------------------------------------- #
