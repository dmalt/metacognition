from pathlib import Path

# setup BIDS root folder
curdir = Path(__file__)
BIDS_ROOT = curdir.parent.parent

# setup source data folder
RAW_DIR = BIDS_ROOT.parent / "raw"

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
ICA_DIR = DERIVATIVES_DIR / "06-apply_ica"
ICA_DIR.mkdir(exist_ok=True)

# create folder for epoched data
EPOCHS_DIR = DERIVATIVES_DIR / "07-make_epochs"
EPOCHS_DIR.mkdir(exist_ok=True)

# create folder for reports
REPORTS_DIR = DERIVATIVES_DIR / "99-reports"
REPORTS_DIR.mkdir(exist_ok=True)

crosstalk_file = str(BIDS_ROOT / "SSS_data" / "ct_sparse.fif")
cal_file = str(BIDS_ROOT / "SSS_data" / "sss_cal.dat")

ev_id = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidence": 5,
}

random_state = 28

if __name__ == "__main__":
    print(f"Current path is {curdir}")
    print(f"BIDS_ROOT is {BIDS_ROOT}")
    print(f"RAW_DIR is {RAW_DIR}")
    print(f"DERIVATIVES_DIR is {DERIVATIVES_DIR}")
    print(f"HP_DIR is {HP_DIR}")
    print(f"REPORTS_DIR is {REPORTS_DIR}")
