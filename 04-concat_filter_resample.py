from operator import attrgetter
from pathlib import PurePath

from mne.io import read_raw_fif
from mne import concatenate_raws

from config import MAXFILTER_DIR, FILTER_DIR
from utils import setup_logging, BidsFname

logger = setup_logging(__file__)

filter_freqs = (1, 100)
resample_freq = 500


def concat_runs(fifs):
    raws = [read_raw_fif(str(f), preload=True) for f in fifs]
    common_ch_names = set.intersection(*[set(r.ch_names) for r in raws])
    for raw in raws:
        raw.pick_channels(list(common_ch_names))
    if len(raws) > 1:
        return concatenate_raws(raws)
    else:
        return raws[0]


def process_fif(fif, subj):
    if isinstance(fif, list):
        raw = concat_runs(fif)
        bids_fname = BidsFname(fif[0].name)
        bids_fname["run"] = None
    elif isinstance(fif, PurePath):
        raw = read_raw_fif(str(fif), preload=True)
        bids_fname = BidsFname(fif.name)

    bids_fname["proc"] = "filt"
    raw.apply_proj()
    raw.filter(
        l_freq=filter_freqs[0],
        h_freq=filter_freqs[1],
        n_jobs=1,
        # skip_by_annotation="edge",  # do not skip bad_acq_skip for now
        pad='symmetric',
    )
    raw.resample(sfreq=resample_freq, n_jobs=1)

    dest_dir = FILTER_DIR / subj.name
    if subj.name == "sub-emptyroom":
        dest_dir.mkdir(exist_ok=True)
        dest_dir = dest_dir / bids_fname.to_string("ses")
    dest_dir.mkdir(exist_ok=True)
    dest_fpath = dest_dir / str(bids_fname)
    raw.save(str(dest_fpath), overwrite=True)


if __name__ == "__main__":
    subjs = MAXFILTER_DIR.glob("sub-*")
    for subj in subjs:
        task_files = sorted(
            subj.rglob("*run-0[1-9]*_meg.fif"), key=attrgetter("name")
        )
        all_files = [f for f in subj.rglob("*_meg.fif") if f not in task_files]
        if task_files:
            all_files.append(task_files)
        for f in all_files:
            if isinstance(f, PurePath):
                logger.info(f"Processing {f.name}")
            elif isinstance(f, list):
                logger.info("Processing")
                for item in f:
                    logger.info(f"\t{item.name}")
            process_fif(f, subj)
