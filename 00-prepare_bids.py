"""
Prepare bids dataset from raw data.

Copy files from raw folder and store them in BIDS-organized folders.

Mark flat segments and channels while copying. Flats are causing
trouble during head position detection for some subjects and files.

Note
----
Some filenames were changed manually to simplify processing, e.g.
cyrillic names for tables and subject names.

"""
import re
from operator import itemgetter
from pathlib import Path
from collections import namedtuple

import pandas as pd

import mne
from mne.io import read_raw_fif
# from mne.preprocessing import mark_flat
from mne_bids import (
    make_bids_basename,
    make_bids_folders,
    make_dataset_description,
    write_raw_bids,
)
from mne.io import read_info

from config import RAW_DIR, BIDS_ROOT, EVENTS_ID
from utils import setup_logging

logger = setup_logging(__file__)
BIDS_ROOT = str(BIDS_ROOT)


FifFile = namedtuple("FifFile", ["path", "type"])


def parse_fif_files(files):
    fif_files = []
    n_task_files = 0
    n_prac_files = 0
    n_er_files = 0
    n_rest_files = 0
    for f in files:
        if re.match(r".*block_?[1-3]{1}\.fif", f.name.lower()):
            fif_files.append(FifFile(str(f), "questions"))
            n_task_files += 1
        elif f.name.lower().endswith("empty_room.fif"):
            fif_files.append(FifFile(str(f), "emptyroom"))
            n_er_files += 1
        elif f.name.lower().endswith(
            "practice.fif"
        ) or f.name.lower().endswith("training.fif"):
            fif_files.append(FifFile(str(f), "practice"))
            n_prac_files += 1
        elif f.name.lower().endswith("resting_state.fif"):
            fif_files.append(FifFile(str(f), "rest"))
            n_rest_files += 1
        else:
            logger.warning(f"Unknown file {f}")

    fif_files.sort()

    if n_task_files == 0:
        logger.warning("No task files")

    if n_prac_files > 1:
        logger.warning("Multiple practice files")
    if n_rest_files > 1:
        logger.warning("multiple rest files")

    return fif_files


def process_fif_files(files, subj_id, overwrite=True):
    """
    Move fif files into BIDS folder structure

    Mark flats and copy files with apropriate naming based on type of MEG
    recording; for task files also find events; append entry to
    participants.tsv

    Parameters
    ----------
    files : list of os.PathLike instances
        fif files with MEG recordings to process
    subj_id : str
        numerical ID of a subject

    """
    fif_files = parse_fif_files(files)
    n_task = 0
    for f in fif_files:
        raw = read_raw_fif(f.path, verbose="ERROR")

        if f.type == "questions":
            base = make_bids_basename(subj_id, task=f.type, run=n_task + 1)
            n_task += 1
        elif f.type in ("rest", "practice"):
            base = make_bids_basename(subject=subj_id, task=f.type)
        elif f.type == "emptyroom":
            meas_date = raw.info["meas_date"]
            d = meas_date.date()
            ses_date = "%04d%02d%02d" % (d.year, d.month, d.day)
            base = make_bids_basename(
                "emptyroom", task="noise", session=ses_date
            )
        if f.type == "questions":
            ev = mne.find_events(raw, min_duration=2 / raw.info["sfreq"])
            ev_id = EVENTS_ID
        else:
            ev = None
            ev_id = None
        # mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)
        write_raw_bids(
            raw,
            base,
            BIDS_ROOT,
            ev,
            ev_id,
            overwrite=overwrite,
            verbose=False,
        )


def convert_subj(subj_path, subj_id, pattern="*.fif"):
    """
    Parameters
    ----------
    subj_path : instance of pathlib.PosixPath
    subj_id : str

    """
    # dst_meg_dir = make_bids_folders(
    #     subject=subj_id, kind="meg", output_path=str(BIDS_ROOT)
    # )

    src_meg_files = subj_path.rglob(pattern)
    # process task data
    process_fif_files(src_meg_files, subj_id)

    # process behavioral data
    src_beh_dir = subj_path.parent / "behavioral_data"
    subj_name = subj_path.name.split("-")[1]  # remove "sub-" prefix
    beh_file = None
    for f in src_beh_dir.iterdir():
        if f.stem.lower().startswith(subj_name.lower()):
            beh_file = f
            break
    if beh_file:
        dst_beh_dir = Path(
            make_bids_folders(subj_id, kind="beh", bids_root=BIDS_ROOT)
        )
        base = make_bids_basename(subj_id, task="questions", suffix="beh.tsv")
        beh_savename = dst_beh_dir / base
        df = pd.read_excel(beh_file)
        df.to_csv(beh_savename, sep="\t", index=False)
    else:
        logger.warning(f"No behavioral data for {subj_id}")


def map_subjects_to_enum_id(subjs):
    """Make subj_ids by enumerating recordings in chronological order"""
    meas_dates = []
    for s in filter(
        lambda s: not s.match("sub-emptyroom"), RAW_DIR.glob("sub-*")
    ):
        # get first fif file and extract measurement date
        info_src = str(next(s.rglob("*.fif")))
        meas_dates.append(
            (s, read_info(info_src, verbose="ERROR")["meas_date"])
        )

    # sort subjects according to their measuremet datetime
    subjs = sorted(meas_dates, key=itemgetter(1))

    # create list of tuples with paths and zero-padded numbers as subj_id
    return [(s[0], f"{i + 1:02}") for i, s in enumerate(subjs)]


if __name__ == "__main__":
    subjs = map_subjects_to_enum_id()
    for s in subjs[9:10]:
        logger.info(f"Renaming {s[0].name} to sub-{s[1]}\n")
        convert_subj(*s, pattern="*state.fif")
    ER_dir = next(RAW_DIR.glob("sub-emptyroom"))
    logger.info("Processing emptyroom data")
    # convert_subj(ER_dir, "emptyroom")

    make_dataset_description(
        path=BIDS_ROOT,
        name="metacognition",
        authors=[
            "Beatriz Martin Luengo",
            "Maria Alekseeva",
            "Dmitrii Altukhov",
            "Yuri Shtyrov",
        ],
    )
