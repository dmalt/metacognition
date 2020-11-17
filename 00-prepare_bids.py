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
from collections import namedtuple
from argparse import ArgumentParser

import pandas as pd

import mne
from mne.io import read_raw_fif

from mne.preprocessing import mark_flat

from mne_bids import BIDSPath, write_raw_bids

from config import RAW_DIR, BIDS_ROOT, EVENTS_ID, subj_ids_file
from utils import setup_logging, SubjectRenamer

logger = setup_logging(__file__)

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
    elif n_prac_files == 0:
        logger.warning("No practice files")
    if n_rest_files > 1:
        logger.warning("multiple rest files")
    elif n_rest_files == 0:
        logger.warning("No rest files")

    return fif_files


def process_fif_files(files, subj_id, overwrite=True, is_mark_flat=False):
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
    n_task = 1
    bids_path_args = {
        "root": str(BIDS_ROOT),
        "extension": ".fif",
        "suffix": "meg",
    }
    for fif_file in fif_files:
        raw = read_raw_fif(fif_file.path, verbose="ERROR")

        bids_path_args["subject"] = subj_id
        bids_path_args["task"] = fif_file.type
        bids_path_args["run"] = None
        bids_path_args["session"] = None

        if fif_file.type == "questions":
            bids_path_args["run"] = n_task
            n_task += 1
        elif fif_file.type == "emptyroom":
            meas_date = raw.info["meas_date"]
            d = meas_date.date()
            ses_date = "%04d%02d%02d" % (d.year, d.month, d.day)
            bids_path_args["subject"] = "emptyroom"
            bids_path_args["task"] = "noise"
            bids_path_args["session"] = ses_date
        bids_path = BIDSPath(**bids_path_args)

        if fif_file.type == "questions":
            ev = mne.find_events(raw, min_duration=2 / raw.info["sfreq"])
            ev_id = EVENTS_ID
        else:
            ev = None
            ev_id = None

        # nonempty annotations with ev_id=None cause crash in write_raw_bids
        raw.set_annotations(None)
        if is_mark_flat:
            mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)

        logger.info(f"Writing {bids_path.basename}")
        write_raw_bids(
            raw, bids_path, ev, ev_id, overwrite=overwrite, verbose=False,
        )


def convert_subj(subj_path, subj_id, pattern="*.fif", is_mark_flat=False):
    """
    Parameters
    ----------
    subj_path : instance of pathlib.PosixPath
    subj_id : str

    """

    src_meg_files = subj_path.rglob(pattern)
    # process meg data
    process_fif_files(src_meg_files, subj_id, is_mark_flat=is_mark_flat)

    # process behavioral data
    src_beh_dir = subj_path.parent / "behavioral_data"
    subj_name = subj_path.name
    beh_file = None
    for f in src_beh_dir.iterdir():
        if f.stem.lower().startswith(subj_name.lower()):
            beh_file = f
            break
    if beh_file:
        base = BIDSPath(
            subj_id,
            task="questions",
            datatype="beh",
            suffix="behav",
            extension=".tsv",
            root=str(BIDS_ROOT),
        )
        base.mkdir()
        beh_savename = str(base)
        df = pd.read_excel(beh_file)
        df.to_csv(beh_savename, sep="\t", index=False)
    else:
        logger.warning(f"No behavioral data for {subj_id}")


if __name__ == "__main__":
    parser = ArgumentParser(description="Copy files to BIDS folders structure")
    renamer = SubjectRenamer(subj_ids_file)

    parser.add_argument(
        "subject",
        choices=list(renamer.subj_ids_map.keys()) + ["emptyroom"],
        help="subject id",
    )
    parser.add_argument(
        "-f",
        "--flat",
        action="store_true",
        help="mark flat segments (takes time)",
    )
    args = parser.parse_args()

    subj_name = args.subject
    subj_id = renamer.subj_ids_map[subj_name]
    subj_path = RAW_DIR / subj_name

    convert_subj(
        subj_path, subj_id, pattern="*.fif", is_mark_flat=args.flat,
    )
    # ER_dir = next(RAW_DIR.glob("sub-emptyroom"))
    # logger.info("Processing emptyroom data")
    # convert_subj(ER_dir, "emptyroom")
