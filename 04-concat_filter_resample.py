"""
Filter and resample data. For task data concatenate runs.

Intended to be used with maxfiltered data but this is not obligatory.

"""
import sys
from typing import List
import warnings

from mne.io import read_raw_fif
from mne import concatenate_raws
from mne_bids import BIDSPath

from config import concat_config, bp_maxfilt, bp_filt, subj_runs
from utils import setup_logging, update_bps, parse_args

logger = setup_logging(__file__)
warnings.simplefilter("ignore", RuntimeWarning)


def concat_runs(bps: List[BIDSPath]):
    raws = [read_raw_fif(str(f.fpath), preload=True) for f in bps]
    common_ch_names = set.intersection(*[set(r.ch_names) for r in raws])
    for raw in raws:
        raw.pick_channels(list(common_ch_names))
    if len(raws) > 1:
        return concatenate_raws(raws)
    else:
        return raws[0]


def process_fif(bp_src, bp_dest):
    if bp_dest.task == "questions":
        raw = concat_runs(bp_src)
    else:
        raw = read_raw_fif(bp_src.fpath, preload=True)

    raw.apply_proj()
    raw.filter(
        l_freq=concat_config["filter_freqs"][0],
        h_freq=concat_config["filter_freqs"][1],
        n_jobs=1,
        # skip_by_annotation="edge",  # do not skip bad_acq_skip for now
        pad=concat_config["pad"],
    )
    raw.resample(sfreq=concat_config["resamp_freq"], n_jobs=1)

    raw.save(bp_dest.fpath, overwrite=True)


if __name__ == "__main__":

    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)
    run = 1 if args.task == "questions" else None

    bp_src, bp_dest = update_bps(
        [bp_maxfilt, bp_filt],
        subject=args.subject,
        task=args.task,
        run=run,
        session=args.session,
    )
    bp_dest.update(run=None)  # since we concatenate all 3 runs
    if args.task == "questions":
        bp_src = [
            bp_src.copy().update(run=int(r)) for r in subj_runs[args.subject]
        ]

    bp_dest.mkdir()
    process_fif(bp_src, bp_dest)
