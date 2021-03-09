from argparse import ArgumentParser

from joblib import Memory
import numpy as np
from mne import read_epochs
from tqdm import tqdm
import pandas as pd

from config import (
    tasks,
    runs,
    subjects,
    er_sessions,
    subj_tasks,
    subj_runs,
    bp_epochs,
)


location = "./cachedir"
memory = Memory(location, verbose=0)


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


def parse_args(description, args, emptyroom=False):
    parser = ArgumentParser(description=description)
    if emptyroom:
        subjects.append("emptyroom")
        tasks.append("noise")
        parser.add_argument(
            "--session", "-s", default="None", choices=er_sessions + ["None"]
        )

    parser.add_argument("subject", choices=subjects)
    parser.add_argument("task", choices=tasks)
    parser.add_argument("--run", "-r", choices=runs + ["None"], default="None")
    args = parser.parse_args(args)

    if emptyroom:
        if args.session == "None":
            args.session = None
        if args.subject == "emptyroom":
            assert args.task == "noise"
            assert args.session in er_sessions
        else:
            assert args.task != "noise"
            assert args.session is None

    if args.run == "None":
        args.run = None
    else:
        args.run = int(args.run)
    return args


LOW_CONF_EPOCH = 24
HIGH_CONF_EPOCH = 44


@memory.cache
def assemble_epochs(ep_type="answer", average=False):
    """Read in epochs"""
    n_channels = 204
    n_times = 1001
    X = np.empty((0, n_channels, n_times))
    y = np.empty(0)
    for subj in tqdm(subjects, desc="Loading epochs"):
        ep_path = bp_epochs.fpath(subject=subj)
        ep = (
            read_epochs(ep_path)
            .interpolate_bads()
            .pick_types(meg="grad")[ep_type]
        )

        # required to merge epochs from differen subjects together
        ep.info["dev_head_t"] = None
        X_low = ep["low"].get_data()
        if average:
            X_low = X_low.mean(axis=0, keepdims=True)
            y_low = LOW_CONF_EPOCH
        else:
            y_low = ep["low"].events[:, 2]
        X_high = ep["high"].get_data()
        if average:
            X_high = X_high.mean(axis=0, keepdims=True)
            y_high = HIGH_CONF_EPOCH
        else:
            y_high = ep["high"].events[:, 2]
        X = np.r_[X, X_low, X_high]
        y = np.r_[y, y_low, y_high]
    return X, y


def get_confidence_level(confidence):
    if confidence == 0:
        confidence_lvl = "lowest"
    elif 10 <= confidence <= 30:
        confidence_lvl = "low"
    elif 40 <= confidence <= 60:
        confidence_lvl = "medium"
    elif 70 <= confidence <= 90:
        confidence_lvl = "high"
    elif confidence == 100:
        confidence_lvl = "highest"
    elif pd.isnull(confidence):
        confidence_lvl = "nan"
    else:
        raise ValueError(f"Bad confidence: {confidence}")
    return confidence_lvl
