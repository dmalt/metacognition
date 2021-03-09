"""
Filter and resample data. For task data concatenate runs.

Intended to be used with maxfiltered data but this is not obligatory.

"""
import sys
import warnings

from mne.io import read_raw_fif
from mne import concatenate_raws

from config import concat_config, bp_maxfilt, bp_filt, subj_runs
from utils import setup_logging
from dataset_specific_utils import parse_args

logger = setup_logging(__file__)
warnings.simplefilter("ignore", RuntimeWarning)


def concat_runs(fif_paths):
    raws = [read_raw_fif(f, preload=True) for f in fif_paths]
    common_ch_names = set.intersection(*[set(r.ch_names) for r in raws])
    for raw in raws:
        raw.pick_channels(list(common_ch_names))
    return concatenate_raws(raws) if len(raws) > 1 else raws[0]


def process_fif(src, dest, is_mult_runs):
    raw = concat_runs(src) if is_mult_runs else read_raw_fif(src, preload=True)
    raw.apply_proj()
    raw.filter(
        l_freq=concat_config["filter_freqs"][0],
        h_freq=concat_config["filter_freqs"][1],
        pad=concat_config["pad"],
    )
    raw.resample(sfreq=concat_config["resamp_freq"])
    raw.save(dest, overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], emptyroom=True)
    subj, task, run, ses = args.subject, args.task, args.run, args.session
    run = 1 if args.task == "questions" else None

    # input
    bp_maxfilt_subj = bp_maxfilt.update(subject=subj, task=task, session=ses)
    # output
    filt = bp_filt.fpath(subject=subj, task=task, session=ses)

    if task == "questions":
        maxfilt = [bp_maxfilt_subj.fpath(run=int(r)) for r in subj_runs[subj]]
    else:
        maxfilt = bp_maxfilt_subj.fpath(run=run)

    filt.parent.mkdir(exist_ok=True)
    process_fif(maxfilt, filt, task == "questions")
