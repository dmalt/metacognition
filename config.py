from pathlib import Path

curdir = Path(__file__)
BIDS_ROOT = curdir.parent.parent

RAW_DIR = BIDS_ROOT.parent / "raw"

DERIVATIVES_DIR = BIDS_ROOT / "derivatives"
DERIVATIVES_DIR.mkdir(exist_ok=True)

# create folder for head position
HP_DIR = DERIVATIVES_DIR / "01-head_positon"
HP_DIR.mkdir(exist_ok=True)

# create folder for head reports
REPORTS_DIR = DERIVATIVES_DIR / "99-reports"
REPORTS_DIR.mkdir(exist_ok=True)

ev_id = {
    "question/second": 1,
    "question/third": 2,
    "fixcross": 3,
    "answer": 4,
    "confidense": 5,
}

if __name__ == "__main__":
    print(f"Current path is {curdir}")
    print(f"BIDS_ROOT is {BIDS_ROOT}")
    print(f"RAW_DIR is {RAW_DIR}")
    print(f"DERIVATIVES_DIR is {DERIVATIVES_DIR}")
    print(f"HP_DIR is {HP_DIR}")
    print(f"REPORTS_DIR is {REPORTS_DIR}")
