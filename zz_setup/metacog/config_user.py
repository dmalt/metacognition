from collections import defaultdict


BIDS_ROOT = "/home/dmalt/Data/metacognition/MEG1/rawdata"

DATASET_NAME = "metacognition"
AUTHORS = (
    [
        "Beatriz Martin Luengo",
        "Maria Alekseeva",
        "Dmitrii Altukhov",
        "Yuri Shtyrov",
    ],
)


EVENTS_ID = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidence": 5,
}

# scores for numerical encoding of events;
# score is added to event numerical id to separate events by confidence level
confidence_trigger_scores = {
    "lowest": 10,
    "low": 20,
    "medium": 30,
    "high": 40,
    "highest": 50,
    "nan": 60,
}

target_bands = {
    # "alpha": (8, 12),
    # "delta": (2, 4),
    # "theta": (4, 8),
    # "beta": (13, 25),
    "alphabeta": (6, 16),
}

# -------- 04-concat_filter_resample -------- #
concat_config = {
    "filter_freqs": (1, 100),
    "resamp_freq": 500,
    "pad": "symmetric",
}

# -------- 05-compute_ica -------- #
ica_config = {
    "random_state": 28,
    "n_components": 0.99,
    "decim": 5,
    "annot_rej": True,
    "max_iter": 1000,
}

epochs_config = dict(
    tmin=-1,
    tmax=1,
    baseline=None,
    reject=None,
    flat=None,
    reject_by_annotation=True,
    on_missing="ignore",
)
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

# -------- 13-compute_sources -------- #
tfr_config = dict(
    freqs=dict(start=1.0, stop=30., step=1.),
    decim=4,
    use_fft=True,
)
# ------------------------------------ #


all_subjects = [
    "01",
    "02",
    "03",
    "04",
    "05",
    "06",
    "07",
    "08",
    "09",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "24",
    "25",
    "26",
    "27",
    "28",
    "29",
    "30",
    "31",
]

bad_subjects = ["02", "20", "07"]
subjects = [s for s in all_subjects if s not in bad_subjects]

tasks = ["questions", "rest", "practice"]
subj_tasks = defaultdict(lambda: tasks)
subj_tasks["01"] = ["questions", "rest"]
subj_tasks["20"] = ["questions", "practice"]

runs = ["01", "02", "03"]
subj_runs = defaultdict(lambda: runs)
subj_runs["01"] = ["01"]  # first subj has everything in one file

er_sessions = [
    "20200229",
    "20200306",
    "20200311",
    "20200319",
    "20200709",
    "20200716",
    "20200721",
    "20200728",
    "20200806",
    "20200813",
    "20200820",
    "20200827",
    "20200908",
    "20200915",
    "20200923",
    "20201001",
]
