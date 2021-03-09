from pathlib import Path
from collections import defaultdict

import numpy as np

from utils import BIDSPathTemplate

DATASET_NAME = ("metacognition",)
AUTHORS = (
    [
        "Beatriz Martin Luengo",
        "Maria Alekseeva",
        "Dmitrii Altukhov",
        "Yuri Shtyrov",
    ],
)

# setup BIDS root folder
curdir = Path(__file__).resolve()
BIDS_ROOT = curdir.parent.parent

# setup source data folder
RAW_DIR = BIDS_ROOT.parent / "raw"
BEH_RAW_DIR = RAW_DIR / "behavioral_data"

DERIVATIVES_DIR = BIDS_ROOT / "derivatives"
HP_DIR           = DERIVATIVES_DIR / "01-head_positon"            # noqa
BADS_DIR         = DERIVATIVES_DIR / "02-maxfilter_bads"          # noqa
MAXFILTER_DIR    = DERIVATIVES_DIR / "03-maxfilter"               # noqa
FILTER_DIR       = DERIVATIVES_DIR / "04-concat_filter_resample"  # noqa
ICA_SOL_DIR      = DERIVATIVES_DIR / "05-compute_ica"             # noqa
ICA_BADS_DIR     = DERIVATIVES_DIR / "06-inspect_ica"             # noqa
ICA_DIR          = DERIVATIVES_DIR / "07-apply_ica"               # noqa
BAD_SEGMENTS_DIR = DERIVATIVES_DIR / "08-mark_bad_segments"       # noqa
EPOCHS_DIR       = DERIVATIVES_DIR / "09-make_epochs"             # noqa
SUBJECTS_DIR     = DERIVATIVES_DIR / "FSF"                        # noqa
COREG_DIR        = DERIVATIVES_DIR / "10-coreg"                   # noqa
FORWARDS_DIR     = DERIVATIVES_DIR / "11-forwards"                # noqa
INVERSE_DIR      = DERIVATIVES_DIR / "12-inverses"                # noqa
SOURCES_DIR      = DERIVATIVES_DIR / "13-sources"                 # noqa
TFR_DIR          = DERIVATIVES_DIR / "15-tfr"                     # noqa
TFR_AVERAGE_DIR  = DERIVATIVES_DIR / "16-average_tfr"             # noqa
REPORTS_DIR      = DERIVATIVES_DIR / "99-reports"                 # noqa

crosstalk_file = str(BIDS_ROOT / "SSS_data" / "ct_sparse.fif")
cal_file = str(BIDS_ROOT / "SSS_data" / "sss_cal.dat")
subj_ids_file = BIDS_ROOT / "code" / "added_subjects.tsv"


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
    "alpha": (8, 12),
    "delta": (2, 4),
    "theta": (4, 8),
    "beta": (13, 25),
}

# bp_template = BIDSPathTemplate(datatype=None, check=False, extension="fif")
bp_root = BIDSPathTemplate(
    root=BIDS_ROOT, datatype="meg", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# only need this to get emptyroom, so no session template
bp_root_json = BIDSPathTemplate(
    root=BIDS_ROOT, datatype="meg", suffix="meg", extension=".json",
    template_vars=["subject", "task", "run"],
)
# -------- 01-compute_head_position -------- #
bp_headpos = BIDSPathTemplate(
    root=HP_DIR, suffix="hp", extension=".pos",
    template_vars=["subject", "task", "run"],
)
# ------------------------------------------ #

# -------- 02-mark_bads_maxfilter -------- #
bp_annot = BIDSPathTemplate(
    root=BADS_DIR, suffix="annot", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
bp_bads = bp_annot.update(suffix="bads", extension="tsv")
# ---------------------------------------- #

# -------- 03-apply_maxfilter -------- #
bp_maxfilt = BIDSPathTemplate(
    root=MAXFILTER_DIR, processing="sss", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
maxfilt_config = {"t_window": "auto"}
# ------------------------------------ #

# -------- 04-concat_filter_resample -------- #
concat_config = {
    "filter_freqs": (1, 100),
    "resamp_freq": 500,
    "pad": "symmetric",
}

bp_filt = BIDSPathTemplate(
    root=FILTER_DIR, processing="filt", suffix="meg", extension="fif",
    template_vars=["subject", "task", "session"],
)
# ------------------------------------------- #

# -------- 05-compute_ica -------- #
ica_config = {
    "random_state": 28,
    "n_components": 0.99,
    "decim": 5,
    "annot_rej": True,
    "max_iter": 1000,
}

bp_ica_sol = BIDSPathTemplate(
    root=ICA_SOL_DIR, processing="filt", suffix="ica", extension=".fif",
    template_vars=["subject", "task"],
)
# -------------------------------- #

# -------- 06-inspect_ica -------- #
bp_ica_bads = BIDSPathTemplate(
    root=ICA_BADS_DIR, processing="filt", suffix="icabads", extension="tsv",
    template_vars=["subject", "task"],
)
# ------------------------------ #

# -------- 07-apply_ica -------- #
bp_ica = BIDSPathTemplate(
    root=ICA_DIR, processing="ica", suffix="meg", extension="fif",
    template_vars=["subject", "task"],
)
# ------------------------------ #

# -------- 08-mark_bad_segments -------- #
bp_annot_final = BIDSPathTemplate(
    root=BAD_SEGMENTS_DIR, processing="ica", suffix="annot", extension="fif",
    template_vars=["subject", "task"],
)
# -------------------------------------- #

# -------- 09-make_epochs -------- #
bp_epochs = BIDSPathTemplate(
    root=EPOCHS_DIR, processing="ica", task="questions", suffix="epo", extension="fif", # noqa
    template_vars=["subject"],
)
bp_beh = BIDSPathTemplate(
    root=BIDS_ROOT, datatype="beh", task="questions", suffix="behav", extension="tsv", # noqa
    template_vars=["subject"]
)
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
bp_anat = BIDSPathTemplate(
    root=BIDS_ROOT, datatype="anat", suffix="T1w", extension="nii.gz",
    template_vars=["subject"],
)
fsf_config = {"openmp": 8}
# --------------------- #

# -------- 10-coreg -------- #
bp_trans = BIDSPathTemplate(
    root=COREG_DIR, suffix="trans", extension="fif",
    template_vars=["subject"],
)
# -------------------------- #

# -------- 11-compute_forward -------- #
fwd_config = {
    "mindist": 5.0,
    "ico": 4,
    "conductivity": (0.3,),
    "spacing": "oct6",
}
bp_fwd = BIDSPathTemplate(
    root=FORWARDS_DIR, acquisition=fwd_config["spacing"], suffix="fwd", extension="fif", # noqa
    template_vars=["subject"]
)
# ------------------------------------ #

# -------- 12-compute_inverse -------- #
bp_inv = BIDSPathTemplate(
    root=INVERSE_DIR, suffix="inv", acquisition=fwd_config["spacing"], extension="fif", # noqa
    template_vars=["subject"],
)

# ------------------------------------ #

# -------- 13-compute_sources -------- #
config_sources = dict(
    baseline_win=[-1, -0.25],
    active_win=[0.25, 1],
)
# ------------------------------------ #

# -------- 13-compute_sources -------- #
bp_tfr = BIDSPathTemplate(
    root=TFR_DIR, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject"],
)
# bp_itc = BIDSPathTemplate(
#     root=TFR_DIR, processing="ica", suffix="itc", extension="h5", # noqa
#     template_vars=["subject"],
# )
tfr_config = dict(
    freqs=dict(start=1.0, stop=30., step=1.),
    decim=4,
    use_fft=True,
)
# ------------------------------------ #


# -------- average_tfr -------- #
bp_tfr_av = BIDSPathTemplate(
    root=TFR_AVERAGE_DIR, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject", "acquisition"],
)
# ----------------------------- #


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

if __name__ == "__main__":
    print(f"Current path is {curdir}")
    print(f"BIDS_ROOT is {BIDS_ROOT}")
    print(f"RAW_DIR is {RAW_DIR}")
    print(f"DERIVATIVES_DIR is {DERIVATIVES_DIR}")
    print(f"HP_DIR is {HP_DIR}")
    print(f"REPORTS_DIR is {REPORTS_DIR}")
    print(f"SUBJECTS_DIR is {SUBJECTS_DIR}")
