from mne.preprocessing import ICA
from mne.io import read_raw_fif
from mne import Report

from config import FILTER_DIR, ICA_SOL_DIR, random_state
from utils import BidsFname, setup_logging

logger = setup_logging(__file__)


def generate_report(raw, ica, report_savepath):
    logger.info("Generatingg report")
    report = Report(verbose=False)

    fig_topo = ica.plot_components(picks=range(ica.n_components_), show=False)
    report.add_figs_to_section(fig_topo, section="ICA", captions="Timeseries")
    report.save(report_savepath, overwrite=True, open_browser=False)


def compute_ica(fif_file):
    bids_fname = BidsFname(fif_file.name)
    subj = bids_fname.to_string("sub")

    if "split" in bids_fname:
        bids_fname["split"] = None

    raw = read_raw_fif(str(fif_file), preload=True)

    ica = ICA(n_components=0.99, random_state=random_state, max_iter=1000)
    if bids_fname["task"] in ("rest", "practice"):
        decim = None
    else:
        decim = 5
    ica.fit(raw, picks="data", decim=decim, reject_by_annotation=True)

    dest_dir = ICA_SOL_DIR / subj
    dest_dir.mkdir(exist_ok=True)
    ica_savepath = dest_dir / (bids_fname.base + "-ica.fif")
    ica.save(ica_savepath)
    report_savepath = dest_dir / (bids_fname.base + "-ica.html")
    generate_report(raw, ica, report_savepath)


if __name__ == "__main__":
    subjs = FILTER_DIR.glob("sub-[0-9][1-9]")
    # subjs = FILTER_DIR.glob("sub-[0-9]6")
    for subj in subjs:
        fif_files = subj.rglob("*_meg.fif")
        for f in fif_files:
            logger.info(f"Processing {f.name}")
            compute_ica(f)
