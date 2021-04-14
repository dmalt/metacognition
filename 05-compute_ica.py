"""
Compute ICA for fif file; Intended for use with filtered and resampled data.

"""
import sys

from mne.preprocessing import ICA
from mne.io import read_raw_fif
from mne import Report

from config import ica_config, bp_filt, bp_ica_sol
from utils import setup_logging
from dataset_specific_utils import parse_args

logger = setup_logging(__file__)


def generate_report(raw, ica, report_savepath):
    logger.info("Generatingg report")
    report = Report(verbose=False)

    fig_topo = ica.plot_components(picks=range(ica.n_components_), show=False)
    report.add_figs_to_section(fig_topo, section="ICA", captions="Timeseries")
    report.save(report_savepath, overwrite=True, open_browser=False)


def compute_ica(fif_path, ica_sol_path, task):
    raw = read_raw_fif(fif_path, preload=True)
    ica = ICA(
        ica_config["n_components"],
        random_state=ica_config["random_state"],
        max_iter=ica_config["max_iter"],
    )
    decim = None if task in ("rest", "practice") else ica_config["decim"]
    ica.fit(
        raw,
        picks="data",
        decim=decim,
        reject_by_annotation=ica_config["annot_rej"],
    )
    ica.save(ica_sol_path)

    report_path = ica_sol_path.with_suffix(".html")
    generate_report(raw, ica, report_path)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], emptyroom=False)
    subj, task = args.subject, args.task

    # input
    filt = bp_filt.fpath(subject=subj, task=task, session=None)
    # output
    ica_sol = bp_ica_sol.fpath(subject=subj, task=task)

    ica_sol.parent.mkdir(exist_ok=True, parents=True)

    compute_ica(filt, ica_sol, task)
