"""Create report for each subject summarizing all processing steps"""
import mne
from mne import Report
from config import BIDS_ROOT, REPORTS_DIR, HP_DIR, BADS_DIR
from mne import set_log_level
from mne.chpi import read_head_pos
from mne.viz import plot_head_positions
from operator import attrgetter

# -------- fix report module so that parse_folder sees meg.fif files -------- #
from report_patch import _get_toc_property, _iterate_files

mne.report._get_toc_property = _get_toc_property
mne.report._iterate_files = _iterate_files
mne.report.VALID_EXTENSIONS.append("meg.fif")
# --------------------------------------------------------------------------- #

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
    bads_files = list((BADS_DIR / subj.name).glob("*-bads.tsv"))
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


def generate_report(subj):
    report = Report(subject=subj.name, title=subj.name)

    report.parse_folder(str(subj / "meg"), render_bem=False)

    # process head positions
    try:
        report = add_head_postions(subj, report)
    except Exception:
        print(f"WARNING: no head postion file for {subj.name}")

    # add bad channels
    report = add_bad_channels(subj, report)

    dest_dir = REPORTS_DIR / subj.name
    dest_dir.mkdir(exist_ok=True)
    savename = dest_dir / (subj.name + "-report.html")
    report.save(str(savename), open_browser=False, overwrite=True)


if __name__ == "__main__":
    subjs = BIDS_ROOT.glob("sub-[0-9][0-9]")
    for s in subjs:
        print(f"Processing {s.name}")
        generate_report(s)
