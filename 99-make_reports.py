"""Create report for each subject summarizing all processing steps

Note
----
requires mne >= 0.20

"""
from operator import attrgetter

import matplotlib.pyplot as plt

import mne
from mne import set_log_level, read_annotations, Report
from mne.io import read_raw_fif
from mne.chpi import read_head_pos, filter_chpi
from mne.viz import plot_head_positions

from config import BIDS_ROOT, REPORTS_DIR, HP_DIR, BADS_DIR, MAXFILTER_DIR
from utils import BidsFname


set_log_level(verbose="ERROR")


def add_head_postions(subj, report):
    hp_files = list((HP_DIR / subj.name).glob("*_hp.pos"))
    hp_files = sorted(hp_files, key=attrgetter("name"))

    figs = list()
    captions = list()
    for f in hp_files:
        captions.append(str(f.relative_to(BIDS_ROOT.parent)))
        pos = read_head_pos(f)
        fig = plot_head_positions(pos, show=False)
        figs.append(fig)
    report.add_figs_to_section(figs, captions, section="Head position")
    return report


def add_bad_channels(subj, report):
    bads_files = list((BADS_DIR / subj.name).rglob("*-bads.tsv"))
    bads_files = sorted(bads_files, key=attrgetter("name"))

    bads_htmls = list()
    captions = list()
    for bads_file in bads_files:
        with open(bads_file, "r") as f:

            bads = (
                "<p style='text-align:center; font-size: 150%'>"
                + ", ".join(f.readline().split("\t"))
                + "</p>"
            )
            bads_htmls.append(bads)
        captions.append(str(bads_file.relative_to(BIDS_ROOT.parent)))
    report.add_htmls_to_section(
        bads_htmls, captions, section="Bad channels after manual inspection"
    )
    return report


def prepare_raw_orig_data(fif_file, subj):
    raw = read_raw_fif(fif_file, preload=True).pick_types(meg=True, exclude=[])
    if subj.name == "sub-emptyroom":
        allow_line_only = True
    else:
        allow_line_only = False
    filter_chpi(raw, allow_line_only=allow_line_only)

    # set bads and annotations
    bads_dir = BADS_DIR / subj.name
    if subj.name == "sub-emptyroom":
        print(fif_file)
        bids_dict = BidsFname(fif_file.name)
        bads_dir = bads_dir / ("ses-" + bids_dict["ses"])
    basename = fif_file.name[: -len("_meg.fif")]
    bads_fpath = bads_dir / (basename + "-bads.tsv")
    with open(bads_fpath, "r") as f:
        bads = f.readline().split("\t")
    raw.info["bads"] = bads

    annotations_fpath = bads_dir / (basename + "-annot.fif")
    annotations = read_annotations(str(annotations_fpath))
    raw.set_annotations(annotations)

    picks_grad = mne.pick_types(raw.info, meg="grad")
    picks_mag = mne.pick_types(raw.info, meg="mag")

    var = raw.get_data(reject_by_annotation="omit").var(axis=1)
    del raw

    return var[picks_mag], var[picks_grad]


def prepare_raw_tsss_data(fif_file, subj):
    raw_tsss = read_raw_fif(fif_file, preload=True).pick_types(
        meg=True, exclude=[]
    )
    picks_grad = mne.pick_types(raw_tsss.info, meg="grad")
    picks_mag = mne.pick_types(raw_tsss.info, meg="mag")
    var = raw_tsss.get_data(reject_by_annotation="omit").var(axis=1)
    del raw_tsss

    return var[picks_mag], var[picks_grad]


def add_maxwell_filtering_figures(subj, report):
    # load original and maxfiltered data
    orig_fifs = list((BIDS_ROOT / subj.name).rglob("*_meg.fif"))
    orig_fifs = sorted(orig_fifs, key=attrgetter("name"))

    maxwell_fifs = list((MAXFILTER_DIR / subj.name).glob("*_meg.fif"))
    maxwell_fifs = sorted(maxwell_fifs, key=attrgetter("name"))

    figs = list()
    captions = list()
    for orig, maxwell in zip(orig_fifs, maxwell_fifs):
        print(orig, maxwell)
        mag_var_orig, grad_var_orig = prepare_raw_orig_data(orig, subj)
        mag_var_tsss, grad_var_tsss = prepare_raw_tsss_data(maxwell, subj)

        fig, axs = plt.subplots(1, 2, sharey=True, tight_layout=True)

        # We can set the number of bins with the `bins` kwarg
        n_bins = 20
        axs[0].hist([grad_var_orig, grad_var_tsss], bins=n_bins)
        axs[0].set_title("Gradiometers")
        axs[0].legend(["Original", "tsss"])

        axs[1].hist([mag_var_orig, mag_var_tsss], bins=n_bins)
        axs[1].set_title("Magnetometers")
        axs[1].legend(["Original", "tsss"])
        figs.append(fig)
        captions.append(maxwell.name)
    report.add_figs_to_section(figs, captions, section="tsss power histogram")
    return report


def generate_report(subj):
    report = Report(subject=subj.name, title=subj.name)

    if subj.name == "sub-emptyroom":
        report.parse_folder(str(subj), render_bem=False)
    else:
        report.parse_folder(str(subj / "meg"), render_bem=False)

    # process head positions
    if subj.name != "sub-emptyroom":
        report = add_head_postions(subj, report)

    # add bad channels
    report = add_bad_channels(subj, report)

    # add maxwell filtering part
    report = add_maxwell_filtering_figures(subj, report)

    # -------- save results -------- #
    dest_dir = REPORTS_DIR / subj.name
    dest_dir.mkdir(exist_ok=True)
    savename = dest_dir / (subj.name + "-report.html")
    report.save(str(savename), open_browser=False, overwrite=True)
    # ------------------------------ #


if __name__ == "__main__":
    subjs = BIDS_ROOT.glob("sub-*")
    # subjs = BIDS_ROOT.glob("sub-emptyroom")
    for s in subjs:
        print(f"Processing {s.name}")
        generate_report(s)
