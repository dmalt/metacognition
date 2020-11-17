"""Tools for dataset manipulation"""
import os.path as op
from pathlib import Path
from collections import OrderedDict
import re
from datetime import datetime
import logging
from logging import getLogger, FileHandler, StreamHandler, Formatter
from typing import Iterable

from mne.viz import plot_topomap
from mne import find_layout, set_log_file, sys_info
from mne_bids import __version__ as mne_bids_version
from mne.io import read_info


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
                ("part", None),
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

        stderr_handler.setLevel(logging.INFO)
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


class SubjectRenamer:
    def __init__(self, ids_file: Path):
        self.subj_ids_file = ids_file
        self.subj_ids_map = OrderedDict()
        if op.exists(self.subj_ids_file):
            self._load()

    def add(self, subj_paths: Iterable[Path]):
        new_subj_ids_map = self._create_new_subject_ids(subj_paths)
        self.subj_ids_map.update(new_subj_ids_map)

    def dump(self):
        with open(self.subj_ids_file, "w") as f:
            for s in self.subj_ids_map:
                f.write("\t".join((s, self.subj_ids_map[s])) + "\n")

    def reverse(self):
        return OrderedDict(
            (self.subj_ids_map[k], k) for k in self.subj_ids_map
        )

    def _load(self):
        with open(self.subj_ids_file, "r") as f:
            for line in f:
                subj_name, subj_id = line.rstrip().split("\t")
                self.subj_ids_map[subj_name] = subj_id

    def _create_new_subject_ids(self, subj_paths: Iterable[Path]):
        """Make subj_ids by enumerating recordings in chronological order"""
        if len(self.subj_ids_map):
            last_subj_name = next(reversed(self.subj_ids_map))
            processed_max_id = int(self.subj_ids_map[last_subj_name])
        else:
            processed_max_id = 0

        subj_paths = self._sort_by_meas_date(subj_paths)

        new_subj_ids_map = OrderedDict()
        i_subj = 1
        for s in subj_paths:
            if s.match("emptyroom"):
                continue
            elif s.name in self.subj_ids_map:
                subj_id = self.subj_ids_map[s.name]
            else:
                subj_id = f"{i_subj + processed_max_id:02}"
                i_subj += 1
            new_subj_ids_map[s.name] = subj_id
        return new_subj_ids_map

    def _sort_by_meas_date(self, subj_paths):
        """Sort a list of paths to subject folders by measurement date"""
        m_dates = []
        for s in subj_paths:
            info_src = str(next(s.rglob("*.fif")))
            m_dates.append(read_info(info_src, verbose="ERROR")["meas_date"])
        return [x for _, x in sorted(zip(m_dates, subj_paths))]
