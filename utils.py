"""Tools for dataset manipulation"""

from pathlib import Path
from collections import OrderedDict
import re
from datetime import datetime
import logging
from logging import getLogger, FileHandler, StreamHandler, Formatter

from mne.viz import plot_topomap
from mne import find_layout, set_log_file, sys_info
from mne_bids import __version__ as mne_bids_version


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

    stderr_handler = StreamHandler()
    file_handler = FileHandler(log_savepath)

    stderr_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    logger.setLevel(logging.INFO)

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
