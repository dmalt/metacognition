from pathlib import Path

curdir = Path(__file__)
BIDS_ROOT = curdir.parent.parent
RAW_DIR = BIDS_ROOT.parent / "raw"

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
