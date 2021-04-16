"""Tools for dataset manipulation"""
from pathlib import Path
from collections import OrderedDict
from functools import wraps
import re
from datetime import datetime
from types import GeneratorType
from inspect import Parameter, Signature

import logging
from logging import getLogger, FileHandler, StreamHandler, Formatter

from mne.viz import plot_topomap, plot_compare_evokeds, tight_layout
from mne import find_layout, set_log_file, sys_info, EvokedArray
from mne_bids import __version__ as mne_bids_version, BIDSPath
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable

from metacog.paths import dirs


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
    log_savepath = (dirs.logs) / log_fname

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

    write_log_header(log_savepath)
    set_log_file(log_savepath, overwrite=False)
    return logger


def write_log_header(log_savepath, width=80, sep="=", alt_sep="-"):
    with open(log_savepath, "a") as log_file:
        log_file.write(sep * width + "\n")
        log_file.write(str(datetime.now()).center(width, sep) + "\n")
        log_file.write(sep * width + "\n")
        sys_info(fid=log_file)
        log_file.write("mne-bids:".ljust(15) + mne_bids_version + "\n")
        log_file.write(alt_sep * width + "\n")


def update_bps(bp_templates, **kwargs):
    return [bp.copy().update(**kwargs) for bp in bp_templates]


def disable(func, *pargs, **kwargs):
    """Decorator for disabing doit tasks

    Effectively sets actions, dependencies and targets to empty lists.

    """

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


class FrozenBIDSPath:
    def __init__(self, *pargs, check=False, **kwargs):
        self._bp = BIDSPath(*pargs, check=check, **kwargs)

    def update(self, *, check=None, **kwargs):
        copy = self.__class__(subject="dummy", check=False)
        copy._bp = self._bp.copy().update(**kwargs)
        return copy

    def copy(self):
        return self

    def __getattr__(self, attr):
        return getattr(self._bp, attr)

    def __repr__(self):
        return repr(self._bp).replace(
            type(self._bp).__name__, type(self).__name__
        )

    def __str__(self):
        return str(self._bp).replace(
            type(self._bp).__name__, type(self).__name__
        )

    def __dir__(self):
        own_dir = dir(type(self)) + list(self.__dict__.keys())
        return own_dir + [
            d
            for d in dir(self._bp)
            if not d.startswith("_") and d not in own_dir
        ]


class BIDSPathTemplate(FrozenBIDSPath):
    def __init__(self, *pargs, check=False, template_vars=set(), **kwargs):
        super().__init__(*pargs, check=check, **kwargs)
        self._template_vars = set(template_vars)
        for var in self._template_vars:
            self._check_template_var(var)
        self._make_fpath_signature()

    def fpath(self, **kwargs):
        # based on recipie 9.16 from the Python Cookbook, 3-d edition
        self._fpath_sig.bind(**kwargs)

        concrete_bp = self.update(**kwargs)
        return super(self.__class__, concrete_bp).__getattr__("fpath")

    def update(self, *, check=None, **kwargs):
        """
        Note
        ----
        When updating BIDS key-value pairs (not template_vars),
        if some of the keys were present template_vars and updated to non-None
        values, these keys are removed from template_vars

        """
        if "template_vars" in kwargs:
            other_template_vars = set(kwargs.pop("template_vars"))
        else:
            other_template_vars = self._template_vars.copy()

        other = super().update(check=check, **kwargs)
        for key, val in kwargs.items():
            if key in self._template_vars:
                other_template_vars.remove(key)
        other._template_vars = other_template_vars
        other._make_fpath_signature()
        return other

    @property
    def template_vars(self):
        return self._template_vars

    def _make_fpath_signature(self):
        params = [
            Parameter(p, Parameter.KEYWORD_ONLY) for p in self._template_vars
        ]
        self._fpath_sig = Signature(params)

    def _check_template_var(self, var):
        if var not in self.entities:
            raise ValueError(
                "Template entities should be in"
                f"{list(self.entities)}; got '{var}'"
            )
        if self.entities[var] is not None:
            raise ValueError(
                "Can only set 'None' entities as the template ones"
                f" ({var} is set to '{self.entities[var]}')"
            )


def read_ica_bads(ica_bads_path, logger):
    with open(ica_bads_path, "r") as f:
        line = f.readline()
        bads = [int(b) for b in line.split("\t")] if line else []
        logger.info(f"Loading BADS from file: {bads}")
    return bads


def write_ica_bads(ica_bads_path, ica, logger):
    with open(ica_bads_path, "w") as f:
        f.write("\t".join([str(ic) for ic in ica.exclude]))
        logger.info(f"Loading BADS from file: {ica.exclude}")


def plot_temporal_clusters(
    good_cluster_inds, evokeds, T_obs, clusters, times, info
):
    colors = {"low": "crimson", "high": "steelblue"}
    linestyles = {"low": "-", "high": "--"}
    #
    # loop over clusters
    for i_clu, clu_idx in enumerate(good_cluster_inds):
        # unpack cluster information, get unique indices
        time_inds, space_inds = np.squeeze(clusters[clu_idx])
        ch_inds = np.unique(space_inds)
        time_inds = np.unique(time_inds)

        # get topography for F stat
        f_map = T_obs[time_inds, ...].mean(axis=0)

        # get signals at the sensors contributing to the cluster
        sig_times = times[time_inds]

        # create spatial mask
        mask = np.zeros((f_map.shape[0], 1), dtype=bool)
        mask[ch_inds, :] = True

        # initialize figure
        fig, ax_topo = plt.subplots(1, 1, figsize=(10, 3))

        # plot average test statistic and mark significant sensors
        f_evoked = EvokedArray(f_map[:, np.newaxis], info, tmin=0)
        f_evoked.plot_topomap(
            times=0,
            mask=mask,
            axes=ax_topo,
            cmap="Reds",
            vmin=np.min,
            vmax=np.max,
            show=False,
            colorbar=False,
            mask_params=dict(markersize=10),
        )
        image = ax_topo.images[0]

        # create additional axes (for ERF and colorbar)
        divider = make_axes_locatable(ax_topo)

        # add axes for colorbar
        ax_colorbar = divider.append_axes("right", size="5%", pad=0.05)
        plt.colorbar(image, cax=ax_colorbar)
        ax_topo.set_xlabel(
            "Averaged F-map ({:0.3f} - {:0.3f} s)".format(*sig_times[[0, -1]])
        )

        # add new axis for time courses and plot time courses
        ax_signals = divider.append_axes("right", size="300%", pad=1.2)
        title = "Cluster #{0}, {1} sensor".format(i_clu + 1, len(ch_inds))
        if len(ch_inds) > 1:
            title += "s (mean)"
        plot_compare_evokeds(
            evokeds,
            title=title,
            picks=ch_inds,
            axes=ax_signals,
            colors=colors,
            linestyles=linestyles,
            show=False,
            split_legend=True,
            truncate_yaxis="auto",
        )

        # plot temporal cluster extent
        ymin, ymax = ax_signals.get_ylim()
        ax_signals.fill_betweenx(
            (ymin, ymax),
            sig_times[0],
            sig_times[-1],
            color="orange",
            alpha=0.3,
        )

        # clean up viz
        tight_layout(fig=fig)
        fig.subplots_adjust(bottom=0.05)
        plt.show()


if __name__ == "__main__":
    path = Path("sub-test_task-test_meg.fif")
    # p = bids_from_path(path)
    # print(p)
