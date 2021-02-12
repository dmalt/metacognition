from pathlib import Path
from collections import defaultdict
from functools import partial

from mne_bids import BIDSPath

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

# create folder for derivatives
DERIVATIVES_DIR = BIDS_ROOT / "derivatives"
DERIVATIVES_DIR.mkdir(exist_ok=True)

# create folder for head position
HP_DIR = DERIVATIVES_DIR / "01-head_positon"
HP_DIR.mkdir(exist_ok=True)

# create folder for bad channels and bad segments annotations for maxfilter
BADS_DIR = DERIVATIVES_DIR / "02-maxfilter_bads"
BADS_DIR.mkdir(exist_ok=True)

# create folder for maxfiltered data
MAXFILTER_DIR = DERIVATIVES_DIR / "03-maxfilter"
MAXFILTER_DIR.mkdir(exist_ok=True)

# create foder for filtered and resampled data
FILTER_DIR = DERIVATIVES_DIR / "04-concat_filter_resample"
FILTER_DIR.mkdir(exist_ok=True)

# create folder for ICA solutions
ICA_SOL_DIR = DERIVATIVES_DIR / "05-compute_ica"
ICA_SOL_DIR.mkdir(exist_ok=True)

# create folder for ICA solutions
ICA_BADS_DIR = DERIVATIVES_DIR / "06-inspect_ica"
ICA_BADS_DIR.mkdir(exist_ok=True)

# create folder for raw data with removed bad ICA components
ICA_DIR = DERIVATIVES_DIR / "07-apply_ica"
ICA_DIR.mkdir(exist_ok=True)

# create folder for bad segments annotations after ICA cleaning
BAD_SEGMENTS_DIR = DERIVATIVES_DIR / "08-mark_bad_segments"
BAD_SEGMENTS_DIR.mkdir(exist_ok=True)

# create folder for epoched data
EPOCHS_DIR = DERIVATIVES_DIR / "09-make_epochs"
EPOCHS_DIR.mkdir(exist_ok=True)

# create folder for reports
REPORTS_DIR = DERIVATIVES_DIR / "99-reports"
REPORTS_DIR.mkdir(exist_ok=True)

# create folder for freesurfer tesselations
SUBJECTS_DIR = DERIVATIVES_DIR / "FSF"
SUBJECTS_DIR.mkdir(exist_ok=True)

# create folder for coregistrations
COREG_DIR = DERIVATIVES_DIR / "10-coreg"
COREG_DIR.mkdir(exist_ok=True)

# create folder for forward models
FORWARDS_DIR = DERIVATIVES_DIR / "11-forwards"
FORWARDS_DIR.mkdir(exist_ok=True)

# create folder for source estimates
SOURCES_DIR = DERIVATIVES_DIR / "12-sources"
SOURCES_DIR.mkdir(exist_ok=True)

crosstalk_file = str(BIDS_ROOT / "SSS_data" / "ct_sparse.fif")
cal_file = str(BIDS_ROOT / "SSS_data" / "sss_cal.dat")
subj_ids_file = BIDS_ROOT / "code" / "added_subjects.tsv"


def iter_files(subjects, runs_return="sep"):
    """
    For each subject generate all valid combinations of bids keywords.

    Parameters
    ----------
    subjects : list of str
        subject IDs
    runs_return : "sep" | "joint" | None
        controls iteration over runs (see Yields section)

    Yields
    ------
    (subj, task, run, ses) tuple if runs_renturn == "sep",
    (subj, task, list of subj runs, ses) tuple if runs_renturn == "joint",
    (subj, task, ses) tuple if runs_renturn == None

    """
    for subj in subjects:
        if subj == "emptyroom":
            task = "noise"
            for ses in er_sessions:
                if runs_return is not None:
                    yield (subj, task, None, ses)
                else:
                    yield (subj, task, ses)
        else:
            for task in subj_tasks[subj]:
                if task == "questions":
                    if runs_return == "sep":
                        for run in subj_runs[subj]:
                            yield (subj, task, run, None)
                    elif runs_return == "joint":
                        yield (subj, task, [r for r in subj_runs[subj]], None)
                    else:
                        yield (subj, task, None)
                else:
                    if runs_return is not None:
                        yield (subj, task, None, None)
                    else:
                        yield (subj, task, None)


EVENTS_ID = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidence": 5,
}


bp_template = BIDSPath(datatype=None, check=False, extension="fif")
bp_root = bp_template.copy().update(
    root=BIDS_ROOT, datatype="meg", suffix="meg"
)
# -------- 01-compute_head_position -------- #
bp_headpos = bp_template.copy().update(
    root=HP_DIR, suffix="hp", extension=".pos"
)
# ------------------------------------------ #

# -------- 02-mark_bads_maxfilter -------- #
bp_annot = bp_template.copy().update(root=BADS_DIR, suffix="annot")
bp_bads = bp_annot.copy().update(suffix="bads", extension="tsv")
# ---------------------------------------- #

# -------- 03-apply_maxfilter -------- #
bp_maxfilt = bp_root.copy().update(root=MAXFILTER_DIR, processing="sss")
maxfilt_config = {"t_window": "auto"}
# ------------------------------------ #

# -------- 04-concat_filter_resample -------- #
concat_config = {
    "filter_freqs": (1, 100),
    "resamp_freq": 500,
    "pad": "symmetric",
}

bp_filt = bp_root.copy().update(
    root=FILTER_DIR, processing="filt", suffix="meg", run=None,
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

bp_ica_sol = bp_filt.copy().update(
    root=ICA_SOL_DIR, suffix="ica", datatype=None
)
# -------------------------------- #

# -------- 06-inspect_ica -------- #
bp_ica_bads = bp_ica_sol.copy().update(
    root=ICA_BADS_DIR, suffix="icabads", extension="tsv"
)
# ------------------------------ #

# -------- 07-apply_ica -------- #
bp_ica = bp_root.copy().update(root=ICA_DIR, processing="ica")
# ------------------------------ #

# -------- 08-mark_bad_segments -------- #
bp_annot_final = bp_ica.copy().update(root=BAD_SEGMENTS_DIR, suffix="annot")
# -------------------------------------- #

# -------- 09-make_epochs -------- #
bp_epochs = bp_ica.copy().update(root=EPOCHS_DIR, suffix="epo")
# -------------------------------- #

# -------- FSF -------- #
# some_code
bp_anat = bp_root.copy().update(
    datatype="anat", suffix="T1w", extension="nii.gz"
)
fsf_config = {"openmp": 8}
# --------------------- #

# -------- 10-coreg -------- #
trans_path = str(COREG_DIR / "sub-{subject}-trans.fif")
# -------------------------- #

# -------- 11-compute_forward -------- #
fwd_config = {
    "mindist": 5.0,
    "ico": 4,
    "conductivity": (0.3,),
    "spacing": "oct6",
}
fwd_path = str(
    FORWARDS_DIR / "sub-{{subject}}_spacing-{spacing}-fwd.fif"
).format(spacing=fwd_config["spacing"])
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

if __name__ == "__main__":
    print(f"Current path is {curdir}")
    print(f"BIDS_ROOT is {BIDS_ROOT}")
    print(f"RAW_DIR is {RAW_DIR}")
    print(f"DERIVATIVES_DIR is {DERIVATIVES_DIR}")
    print(f"HP_DIR is {HP_DIR}")
    print(f"REPORTS_DIR is {REPORTS_DIR}")
    print(f"SUBJECTS_DIR is {SUBJECTS_DIR}")
