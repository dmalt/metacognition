"""Tools for dataset manipulation"""

from pathlib import Path
from collections import OrderedDict

from mne.viz import plot_topomap
from mne import find_layout, set_log_file


class BidsFname:
    def __init__(self, fname):
        bids_split = fname.split("_")
        base = bids_split[:-1]  # TODO: what if there's no suffix?
        self.mod, self.ext = bids_split[-1].split(".")
        self._bids_dict = OrderedDict(
            (f.split("-")[0], f.split("-")[1]) for f in base
        )

    def __repr__(self):
        return self.to_string()

    def __copy__(self):
        return BidsFname(str(self))

    def __contains__(self, key):
        return key in self._bids_dict

    def copy(self):
        return self.__copy__()

    def to_string(self, part=None):
        if not part:
            base_list = [self.to_string(k) for k in self._bids_dict]
            suffix_list = [self.to_string("suffix")]
            return "_".join(base_list + suffix_list)
        elif part in self._bids_dict:
            return "-".join([part, self._bids_dict[part]])
        elif part == "mod":
            return self.mod
        elif part == "ext":
            return self.ext
        elif part == "suffix":
            return ".".join([self.mod, self.ext])
        elif part == "base":
            base_list = [self.to_string(k) for k in self._bids_dict]
            return "_".join(base_list)

    def __getitem__(self, key):
        if key in self._bids_dict:
            return self._bids_dict[key]
        else:
            raise AttributeError(f"Bad attribute {key}")

    def __setitem__(self, key, val):
        if not isinstance(val, str) and val is not None:
            raise AttributeError(
                "Can's set attribute."
                f" Value type shoud be str or None; got {type(val)} insted"
            )
        if val is None and key in self._bids_dict:
            del self._bids_dict[key]
        else:
            self._bids_dict[key] = val

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


def dict_from_bids_fname(fname):
    bids_split = fname.split("_")
    base = bids_split[:-1]
    mod, ext = bids_split[-1].split(".")
    bids_dict = OrderedDict((f.split("-")[0], f.split("-")[1]) for f in base)
    return bids_dict


def output_log(script_name):
    """Save mne-python log to a file in logs folder"""
    log_savepath = (Path("logs")) / (Path(script_name).stem + ".log")
    set_log_file(log_savepath, overwrite=True)
