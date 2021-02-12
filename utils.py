"""Tools for dataset manipulation"""
from argparse import ArgumentParser
from pathlib import Path
from collections import OrderedDict
from functools import wraps
import re
from datetime import datetime
from types import GeneratorType


import logging
from logging import getLogger, FileHandler, StreamHandler, Formatter

from mne.viz import plot_topomap
from mne import find_layout, set_log_file, sys_info
from mne_bids import __version__ as mne_bids_version, BIDSPath

from config import tasks, runs, subjects, er_sessions


def bids_from_path(path: Path):
    bids_path_kwargs = {}

    bids_names = OrderedDict(
        [
            ("sub", "subject"),
            ("ses", "session"),
            ("task", "task"),
            ("acq", "acquisition"),
            ("run", "run"),
            ("proc", "processing"),
            ("rec", "recording"),
            ("space", "space"),
            ("split", "split"),
        ]
    )

    dir_ses = None
    if path.match("*/sub-*/ses-*/*/*.*"):
        bids_path_kwargs["datatype"] = path.parent.name
        dir_subj = path.parent.parent.parent.name.split("-")[1]
        dir_ses = path.parent.parent.name.split("-")[1]
        bids_path_kwargs["root"] = path.parent.parent.parent.parent
    elif path.match("*/sub-*/ses-*/*.*"):
        dir_ses = path.parent.name.split("-")[1]
        dir_subj = path.parent.parent.name.split("-")[1]
        bids_path_kwargs["root"] = path.parent.parent.parent
    elif path.match("*/sub-*/*/*.*"):
        bids_path_kwargs["datatype"] = path.parent.name
        dir_subj = path.parent.parent.name.split("-")[1]
        bids_path_kwargs["root"] = path.parent.parent.parent
    elif path.match("*/sub-*/*.*"):
        dir_subj = path.parent.name.split("-")[1]
        bids_path_kwargs["root"] = path.parent.parent

    match = re.match(r"([a-z0-9_-]+)_([a-z]+)\.([a-z]+)$", path.name)
    if match:
        bids_path_kwargs["suffix"], bids_path_kwargs["extension"] = (
            match.group(2),
            match.group(3),
        )
        base = match.group(1)
    else:
        base = path.name

    bids_split = base.split("_")

    # iterator fuss is to ensure the correct order in fname
    dict_iterator = iter(bids_names)
    for s in bids_split:
        try:
            key, val = s.split("-")
        except ValueError:
            raise ValueError(f"Bad filename format: {path}")

        # fast-forward iterator
        for allowed_key in dict_iterator:
            if allowed_key == key:
                break
        else:
            raise ValueError(f"Bad filename format: {path}")

        if key == "sub":
            assert dir_subj == val, (
                "Subject id in filename and containing folder mismatch:"
                f" {val} != {dir_subj}"
            )
        if key == "ses" and dir_ses is not None:
            assert dir_ses == val, (
                "Session in filename and containing folder mismatch:"
                f" {val} != {dir_ses}"
            )

        bids_path_kwargs[bids_names[key]] = val
    return BIDSPath(**bids_path_kwargs)


class BidsFname:
    def __init__(self, fname):
        match = re.match(r"([a-z0-9_-]+)_([a-z]+)\.([a-z]+)$", fname)
        if match:
            self.mod, self.ext = match.group(2), match.group(3)
            base = match.group(1)
        else:
            base = fname
            self.mod = None
            self.ext = None

        bids_split = base.split("_")

        self._bids_dict = OrderedDict(
            [
                ("sub", None),
                ("ses", None),
                ("task", None),
                ("acq", None),
                ("run", None),
                ("proc", None),
                ("space", None),
                ("recording", None),
                ("split", None),
            ]
        )
        for s in bids_split:
            try:
                key, val = s.split("-")
            except ValueError:
                raise ValueError(f"Bad filename format: {fname}")
            if key in self._bids_dict:
                self._bids_dict[key] = val
            else:
                raise KeyError(f"{key} is not allowed by BIDS format")

    def __repr__(self):
        return self.to_string()

    def __copy__(self):
        new_obj = BidsFname(str(self))
        if self.mod:
            new_obj.mod = self.mod
        if self.ext:
            new_obj.ext = self.ext
        return new_obj

    def __contains__(self, key):
        return key in self._bids_dict and self._bids_dict[key]

    def copy(self):
        return self.__copy__()

    def to_string(self, part=None):
        if part is None:
            base_str = self.to_string("base")
            suffix_str = self.to_string("suffix")
            if base_str and suffix_str:
                return "_".join([base_str, suffix_str])
            elif base_str:
                return base_str
            elif suffix_str:
                return suffix_str
            else:
                return ""
        elif part in self._bids_dict:
            if self._bids_dict[part] is not None:
                return "-".join([part, self._bids_dict[part]])
            else:
                return ""
        elif part == "mod":
            return self.mod if self.mod else ""
        elif part == "ext":
            return self.ext if self.ext else ""
        elif part == "suffix":
            if self.mod and self.ext:
                return ".".join([self.mod, self.ext])
            else:
                return ""
        elif part == "base":
            return "_".join(
                [
                    self.to_string(k)
                    for k in self._bids_dict
                    if self.to_string(k)
                ]
            )

    def __getitem__(self, key):
        if key in self._bids_dict:
            return self._bids_dict[key]
        else:
            raise KeyError(f"Bad key {key}")

    def __setitem__(self, key, val):
        if not isinstance(val, str) and val is not None:
            raise ValueError(
                "Can's set attribute."
                f" Value type shoud be str or NoneType; got {type(val)} insted"
            )
        if key in self._bids_dict:
            self._bids_dict[key] = val
        else:
            raise KeyError(f"{key} is not allowed by BIDS format")

    @property
    def base(self):
        return self.to_string("base")

    @property
    def suffix(self):
        return self.to_string("suffix")


def plot_grads(data, info):
    names = [info["chs"][i]["ch_name"] for i in range(len(info["chs"]))]
    av_data = data.reshape(-1, 2).mean(axis=1)
    print(av_data.shape)
    av_names = [n[:-1] for n in names[::2]]
    layout = find_layout(info)
    pos = layout.pos[::2, :2]
    plot_topomap(av_data, pos, names=av_names, show_names=True)


def setup_logging(script_name):
    """Save mne-python log to a file in logs folder"""
    log_basename = Path(script_name).stem
    log_fname = log_basename + ".log"
    log_savepath = (Path("logs")) / log_fname

    logger = getLogger(log_basename)
    logger.setLevel(logging.INFO)

    if not logger.hasHandlers():
        stderr_handler = StreamHandler()
        file_handler = FileHandler(log_savepath)

        stderr_handler.setLevel(logging.WARNING)
        file_handler.setLevel(logging.INFO)

        fmt = Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        stderr_handler.setFormatter(fmt)
        file_handler.setFormatter(fmt)

        logger.addHandler(stderr_handler)
        logger.addHandler(file_handler)

    with open(log_savepath, "a") as log_file:
        log_file.write("=" * 80 + "\n")
        log_file.write(str(datetime.now()).center(80, "=") + "\n")
        log_file.write("=" * 80 + "\n")
        sys_info(fid=log_file)
        log_file.write("mne-bids:".ljust(15) + mne_bids_version + "\n")
        log_file.write("-" * 80 + "\n")
    set_log_file(log_savepath, overwrite=False)
    return logger


def update_bps(bp_templates, **kwargs):
    return [bp.copy().update(**kwargs) for bp in bp_templates]


def parse_args(description, args, is_applied_to_er=False):
    parser = ArgumentParser(description=description)
    if is_applied_to_er:
        subjects.append("emptyroom")
        tasks.append("noise")
        parser.add_argument(
            "--session", "-s", default="None", choices=er_sessions + ["None"]
        )

    parser.add_argument("subject", choices=subjects)
    parser.add_argument("task", choices=tasks)
    parser.add_argument("--run", "-r", choices=runs + ["None"], default="None")
    args = parser.parse_args(args)

    if is_applied_to_er:
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


def disable(func, *pargs, **kwargs):
    @wraps(func)
    def inner(*pargs, **kwargs):
        res = func(*pargs, **kwargs)
        d = {"actions": [], "file_dep": [], "targets": [], "doc": "DISABLED"}
        if isinstance(res, GeneratorType):
            for r in res:
                r.update(d)
                yield r
        else:
            res.update(d)
            return res

    inner.__doc__ = (
        "DISABLED! " + inner.__doc__ if inner.__doc__ else "DISABLED!"
    )
    return inner


if __name__ == "__main__":
    path = Path("sub-test_task-test_meg.fif")
    p = bids_from_path(path)
    print(p)
