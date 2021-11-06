from argparse import ArgumentParser

from joblib import Memory
import numpy as np
from mne import read_epochs
from tqdm import tqdm
import pandas as pd

from metacog import bp
from metacog.config_parser import cfg


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
    (subj, task, run, ses) tuple if runs_return == "sep",
    (subj, task, list of subj runs, ses) tuple if runs_renturn == "joint",
    (subj, task, ses) tuple if runs_renturn == None

    """
    for subj in cfg.subjects:
        if subj == "emptyroom":
            task = "noise"
            for ses in cfg.er_sessions:
                if runs_return is not None:
                    yield (subj, task, None, ses)
                else:
                    yield (subj, task, ses)
        else:
            for task in cfg.subj_tasks[subj]:
                if task == cfg.subj_tasks[subj][0]:
                    if runs_return == "sep":
                        for run in cfg.subj_runs[subj]:
                            yield (subj, task, run, None)
                    elif runs_return == "joint":
                        yield (
                            subj,
                            task,
                            [r for r in cfg.subj_runs[subj]],
                            None,
                        )
                    else:
                        yield (subj, task, None)
                else:
                    if runs_return is not None:
                        yield (subj, task, None, None)
                    else:
                        yield (subj, task, None)


def parse_args(description, args, emptyroom=False):
    parser = ArgumentParser(description=description)
    tasks_cat = {t for s in cfg.subjects for t in cfg.subj_tasks[s]}
    runs_cat = {t for s in cfg.subjects for t in cfg.subj_runs[s]}
    if emptyroom:
        cfg.subjects.append("emptyroom")
        tasks_cat.add("noise")
        parser.add_argument(
            "--session",
            "-s",
            default="None",
            choices=cfg.er_sessions + ["None"],
        )

    parser.add_argument("subject", choices=cfg.subjects)
    parser.add_argument("task", choices=tasks_cat)
    parser.add_argument(
        "--run", "-r", choices=runs_cat | {"None"}, default="None"
    )
    args = parser.parse_args(args)

    if emptyroom:
        if args.session == "None":
            args.session = None
        if args.subject == "emptyroom":
            assert args.task == "noise"
            assert args.session in cfg.er_sessions
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
def assemble_epochs(ep_type="answer", average=False, ch_type="grad"):
    """Read in epochs"""
    if ch_type == "grad":
        n_channels = 204
    elif ch_type == "mag":
        n_channels = 102
    else:
        raise AttributeError
    n_times = 1001
    X = np.empty((0, n_channels, n_times))
    y = np.empty(0)
    for subj in tqdm(cfg.subjects, desc="Loading epochs"):
        ep_path = bp.epochs.fpath(subject=subj)
        ep = (
            read_epochs(ep_path)
            .interpolate_bads()
            .pick_types(meg=ch_type)[ep_type]
        )
        ep.apply_baseline()

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


@memory.cache
def assemble_epochs_new(
    kind="answer", average=False, baseline=(-0.2, 0), ch_type="grad"
):
    """Read in epochs"""
    X, dfs = [], []
    for subj in tqdm(cfg.subjects, desc="Loading epochs"):
        fp = bp.epochs.fpath(subject=subj)
        ep = read_epochs(fp).interpolate_bads().pick_types(meg=ch_type)[kind]
        ep.apply_baseline(baseline=baseline)
        metadata = ep.metadata
        metadata["subject"] = subj
        dfs.append(metadata)
        X.append(ep.get_data())

    metadata = pd.concat(dfs)
    X = np.concatenate(X)
    return X, metadata, ep.times, ep.info


def get_question_data(i_question, df):
    row = df.loc[i_question]
    try:
        confidence = int(row["оценка"])
    except ValueError:
        confidence = np.nan
    if row["ответ"] in ("1", "2", "3"):
        is_correct = False
    elif row["ответ"] == "c" or row["ответ"] == "с":
        is_correct = True
    else:
        is_correct = np.nan
    try:
        question_num = int(row["question№"])
    except ValueError:
        question_num = np.nan
    return confidence, is_correct, question_num


def get_events_metadata(events, beh_df):
    """
    Get behavioral metadata for each event

    Since each question corresponds to multiple events, we need to assign
    the same metadata to events within one question. Therefore we pick the next
    question only when the new event is of "confidence" type
    """
    assert len(events[events[:, 2] == cfg.EVENTS_ID["answer"]]) == len(beh_df)
    assert len(events[events[:, 2] == cfg.EVENTS_ID["fixcross"]]) == len(
        beh_df
    )
    i_question = 0
    beh_data = {"confidence": [], "is_correct": [], "question_num": []}
    for i, ev in enumerate(events):
        if i_question == 0 or ev[2] == cfg.EVENTS_ID["question/second"]:
            confidence, is_correct, question_num = get_question_data(
                i_question, beh_df
            )
        if ev[2] == cfg.EVENTS_ID["confidence"]:
            i_question += 1
        beh_data["confidence"].append(confidence)
        beh_data["is_correct"].append(is_correct)
        beh_data["question_num"].append(question_num)

    metadata = pd.DataFrame(beh_data)
    return metadata
