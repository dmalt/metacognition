"""
Prepare bids dataset from raw data.

Mark flat segments and channels while copying. Flats are causing
trouble during head position detection for some subjects and files.

Note
----
Some filenames were changed manually to simplify processing, e.g.
cyrillic names for tables and subject names.

mne.__version__ = 0.19.2
At present mne-bids doesn't work for 0.20

"""
import mne
from mne.io import read_raw_fif
from mne_bids import (
    make_bids_basename,
    make_bids_folders,
    make_dataset_description,
    write_raw_bids,
)
from mne.io import read_info
from mne.preprocessing import mark_flat
from config import RAW_DIR, BIDS_ROOT, ev_id
from operator import itemgetter
from datetime import datetime
import pandas as pd
from pathlib import Path

mne.set_log_level(verbose="ERROR")
BIDS_ROOT = str(BIDS_ROOT)


def parse_fif_files(files, subj_id):
    task_files = []
    prac_files = []
    er_files = []
    rest_files = []
    for f in files:
        if f.name.lower().startswith("block"):
            task_files.append(str(f))
        elif f.name.lower() == "empty_room.fif":
            er_files.append(str(f))
        elif f.name.lower() == "practice.fif":
            prac_files.append(str(f))
        elif f.name.lower() == "resting_state.fif":
            rest_files.append(str(f))
        else:
            print(f"Unknown file {f}")

    task_files.sort()

    if len(task_files) == 0:
        print(f"WARNING: no task files for sub-{subj_id}")

    res = {}
    for group, kind in zip(
        (prac_files, rest_files, er_files), ("practice", "RS", "ER"),
    ):
        if len(group) >= 1:
            res[kind] = group[0]
            if len(group) > 1:
                print(f"WARNING: multiple {kind} files for sub-{subj_id}")
        else:
            print(f"WARNING: no {kind} files for sub-{subj_id}")
            res[kind] = None

    return task_files, res["practice"], res["RS"], res["ER"]


def process_fif_files(files, subj_id):
    task_files, prac_file, rest_file, er_file = parse_fif_files(files, subj_id)

    if task_files:
        for i, f in enumerate(task_files):
            base = make_bids_basename(subj_id, task="questions", run=i + 1)
            raw = read_raw_fif(f)
            mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)
            ev = mne.find_events(raw, shortest_event=1)
            write_raw_bids(
                raw, base, BIDS_ROOT, ev, ev_id, overwrite=True, verbose=False
            )

    # process practice file
    if prac_file:
        base = make_bids_basename(subject=subj_id, task="practice")
        raw = read_raw_fif(prac_file)
        mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)
        write_raw_bids(raw, base, BIDS_ROOT, overwrite=True, verbose=False)

    # process resting state file
    if rest_file:
        base = make_bids_basename(subject=subj_id, task="rest")
        raw = read_raw_fif(rest_file)
        mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)
        write_raw_bids(raw, base, BIDS_ROOT, overwrite=True, verbose=False)

    # process empty room file
    if er_file:
        meas_date = read_info(er_file)["meas_date"]
        d = datetime.fromtimestamp(meas_date[0]).date()
        ses_date = "%04d%02d%02d" % (d.year, d.month, d.day)
        base = make_bids_basename("emptyroom", task="noise", session=ses_date)
        raw = read_raw_fif(er_file)
        mark_flat(raw, min_duration=0.1, picks="data", bad_percent=90)
        write_raw_bids(raw, base, BIDS_ROOT, overwrite=True, verbose=False)


def convert_subj(subj_path, subj_id):
    # dst_meg_dir = make_bids_folders(
    #     subject=subj_id, kind="meg", output_path=str(BIDS_ROOT)
    # )

    src_meg_files = subj_path.rglob("*.fif")
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
            make_bids_folders(subj_id, kind="beh", output_path=BIDS_ROOT)
        )
        base = make_bids_basename(subj_id, task="questions", suffix="beh.tsv")
        beh_savename = dst_beh_dir / base
        df = pd.read_excel(beh_file)
        df.to_csv(beh_savename, sep="\t", index=False)
    else:
        print(f"WARNING: no behavioral data for {subj_id}")


def map_subjects_to_enum_id(subjs):
    """make subj_ids by enumerating recordings in chronological order"""
    meas_dates = []
    for s in subjs:
        # get first fif file and extract measurement date
        info_src = str(next(s.rglob("*.fif")))
        meas_dates.append((s, read_info(info_src)["meas_date"]))

    # sort subjects according to their measuremet datetime
    subjs = sorted(meas_dates, key=itemgetter(1))

    # create list of tuples with paths and zero-padded numbers as subj_id
    return [(s[0], f"{i + 1:02}") for i, s in enumerate(subjs)]


if __name__ == "__main__":
    subjs = map_subjects_to_enum_id(RAW_DIR.glob("sub-*"))
    for s in subjs:
        print(f"Processing {s[0].name}")
        convert_subj(*s)

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
