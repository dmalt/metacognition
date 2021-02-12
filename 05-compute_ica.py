"""
Compute ICA for fif file; Intended for use with filtered and resampled data.

"""
import sys

from mne.preprocessing import ICA
from mne.io import read_raw_fif
from mne import Report

from config import (
    ica_config,
    bp_filt,
    bp_ica_sol,
)
from utils import setup_logging, update_bps, parse_args

logger = setup_logging(__file__)


def generate_report(raw, ica, report_savepath):
    logger.info("Generatingg report")
    report = Report(verbose=False)

    fig_topo = ica.plot_components(picks=range(ica.n_components_), show=False)
    report.add_figs_to_section(fig_topo, section="ICA", captions="Timeseries")
    report.save(report_savepath, overwrite=True, open_browser=False)


def compute_ica(bp_src, sol_bp):
    raw = read_raw_fif(str(bp_src.fpath), preload=True)
    ica = ICA(
        ica_config["n_components"],
        random_state=ica_config["random_state"],
        max_iter=ica_config["max_iter"],
    )
    decim = (
        None if sol_bp.task in ("rest", "practice") else ica_config["decim"]
    )
    ica.fit(
        raw,
        picks="data",
        decim=decim,
        reject_by_annotation=ica_config["annot_rej"],
    )
    ica.save(str(sol_bp))

    report_bidspath = sol_bp.copy().update(extension=".html")
    generate_report(raw, ica, str(report_bidspath))


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)

    bp_src, bp_dest = update_bps(
        [bp_filt, bp_ica_sol],
        subject=args.subject,
        task=args.task,
        session=args.session,
    )
    bp_dest.mkdir(exist_ok=True)
    compute_ica(bp_src, bp_dest)
