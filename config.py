from collections import defaultdict
from pathlib import Path
from types import SimpleNamespace

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

dirs = SimpleNamespace()
# setup BIDS root folder
dirs.current = Path(__file__).resolve()
dirs.bids_root = dirs.current.parent.parent

# setup source data folder
dirs.raw          = dirs.bids_root.parent / "raw"                   # noqa
dirs.beh_raw      = dirs.raw / "behavioral_data"                    # noqa

dirs.derivatives  = dirs.bids_root   / "derivatives"                # noqa
dirs.hp           = dirs.derivatives / "01-head_positon"            # noqa
dirs.bads         = dirs.derivatives / "02-maxfilter_bads"          # noqa
dirs.maxfilter    = dirs.derivatives / "03-maxfilter"               # noqa
dirs.filter       = dirs.derivatives / "04-concat_filter_resample"  # noqa
dirs.ica_sol      = dirs.derivatives / "05-compute_ica"             # noqa
dirs.ica_bads     = dirs.derivatives / "06-inspect_ica"             # noqa
dirs.ica          = dirs.derivatives / "07-apply_ica"               # noqa
dirs.bad_segments = dirs.derivatives / "08-mark_bad_segments"       # noqa
dirs.epochs       = dirs.derivatives / "09-make_epochs"             # noqa
dirs.subjects     = dirs.derivatives / "FSF"                        # noqa
dirs.coreg        = dirs.derivatives / "10-coreg"                   # noqa
dirs.forwards     = dirs.derivatives / "11-forwards"                # noqa
dirs.inverse      = dirs.derivatives / "12-inverses"                # noqa
dirs.sources      = dirs.derivatives / "13-sources"                 # noqa
dirs.tfr          = dirs.derivatives / "15-tfr"                     # noqa
dirs.tfr_average  = dirs.derivatives / "16-average_tfr"             # noqa
dirs.reports      = dirs.derivatives / "99-reports"                 # noqa

crosstalk_file = str(dirs.bids_root / "SSS_data" / "ct_sparse.fif")
cal_file = str(dirs.bids_root / "SSS_data" / "sss_cal.dat")
subj_ids_file = dirs.bids_root / "code" / "added_subjects.tsv"


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
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# only need this to get emptyroom, so no session template
bp_root_json = BIDSPathTemplate(
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".json",
    template_vars=["subject", "task", "run"],
)
# -------- 01-compute_head_position -------- #
bp_headpos = BIDSPathTemplate(
    root=dirs.hp, suffix="hp", extension=".pos",
    template_vars=["subject", "task", "run"],
)
# ------------------------------------------ #

# -------- 02-mark_bads_maxfilter -------- #
bp_annot = BIDSPathTemplate(
    root=dirs.bads, suffix="annot", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
bp_bads = bp_annot.update(suffix="bads", extension="tsv")
# ---------------------------------------- #

# -------- 03-apply_maxfilter -------- #
bp_maxfilt = BIDSPathTemplate(
    root=dirs.maxfilter, processing="sss", suffix="meg", extension=".fif",
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
    root=dirs.filter, processing="filt", suffix="meg", extension="fif",
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
    root=dirs.ica_sol, processing="filt", suffix="ica", extension=".fif",
    template_vars=["subject", "task"],
)
# -------------------------------- #

# -------- 06-inspect_ica -------- #
bp_ica_bads = BIDSPathTemplate(
    root=dirs.ica_bads, processing="filt", suffix="icabads", extension="tsv",
    template_vars=["subject", "task"],
)
# ------------------------------ #

# -------- 07-apply_ica -------- #
bp_ica = BIDSPathTemplate(
    root=dirs.ica, processing="ica", suffix="meg", extension="fif",
    template_vars=["subject", "task"],
)
# ------------------------------ #

# -------- 08-mark_bad_segments -------- #
bp_annot_final = BIDSPathTemplate(
    root=dirs.bad_segments, processing="ica", suffix="annot", extension="fif",
    template_vars=["subject", "task"],
)
# -------------------------------------- #

# -------- 09-make_epochs -------- #
bp_epochs = BIDSPathTemplate(
    root=dirs.epochs, processing="ica", task="go", suffix="epo", extension="fif", # noqa
    template_vars=["subject"],
)
bp_beh = BIDSPathTemplate(
    root=dirs.bids_root, datatype="beh", task="questions", suffix="behav", extension="tsv", # noqa
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
    root=dirs.bids_root, datatype="anat", suffix="T1w", extension="nii.gz",
    template_vars=["subject"],
)
fsf_config = {"openmp": 8}
# --------------------- #

# -------- 10-coreg -------- #
bp_trans = BIDSPathTemplate(
    root=dirs.coreg, suffix="trans", extension="fif",
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
    root=dirs.forwards, acquisition=fwd_config["spacing"], suffix="fwd", extension="fif", # noqa
    template_vars=["subject"]
)
# ------------------------------------ #

# -------- 12-compute_inverse -------- #
bp_inv = BIDSPathTemplate(
    root=dirs.inverse, suffix="inv", acquisition=fwd_config["spacing"], extension="fif", # noqa
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
    root=dirs.tfr, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject"],
)
# bp_itc = BIDSPathTemplate(
#     root=dirs.tfr, processing="ica", suffix="itc", extension="h5", # noqa
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
    root=dirs.tfr_average, processing="ica", suffix="tfr", extension="h5", # noqa
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
    print(f"Current path is {dirs.current}")
    print(f"dirs.bids_root is {dirs.bids_root}")
    print(f"dirs.raw is {dirs.raw}")
    print(f"dirs.derivatives is {dirs.derivatives}")
    print(f"dirs.hp is {dirs.hp}")
    print(f"dirs.reports is {dirs.reports}")
    print(f"dirs.subjects is {dirs.subjects}")
