"""Create and manually mark bad epochs."""
import sys
from pathlib import Path
from itertools import product

import pandas as pd
import numpy as np

from mne import Epochs, find_events, read_annotations
from mne.io import read_raw_fif

from config import (
    BIDS_ROOT,
    EPOCHS_DIR,
    EVENTS_ID,
    bp_ica,
    bp_annot_final,
    bp_epochs,
)
from utils import setup_logging, bids_from_path, parse_args, update_bps

logger = setup_logging(__file__)

confidence_trigger_scores = {
    "lowest": 10,
    "low": 20,
    "medium": 30,
    "high": 40,
    "highest": 50,
    "nan": 60,
}

ev_id_confidence = {}
for trig, conf_lvl in product(EVENTS_ID, confidence_trigger_scores):
    ev_id_confidence[trig + "/" + conf_lvl] = (
        EVENTS_ID[trig] + confidence_trigger_scores[conf_lvl]
    )


def transform_events(events, subj_name):

    beh_fpath = next((BIDS_ROOT / subj_name / "beh").glob("*.tsv"))
    beh_df = pd.read_csv(beh_fpath, sep="\t")
    # assert len(events[events[:, 2] == EVENTS_ID["answer"]]) == len(beh_df)
    # assert len(events[events[:, 2] == EVENTS_ID["fixcross"]]) == len(beh_df)

    i_question = 0
    for i, ev in enumerate(events):
        if i_question == 0 or ev[2] == EVENTS_ID["question/second"]:
            try:
                confidence = int(beh_df.loc[i_question, "оценка"])
            except ValueError:
                confidence = np.nan
            if confidence == 0:
                confidence_lvl = "lowest"
            elif 10 <= confidence <= 30:
                confidence_lvl = "low"
            elif 40 <= confidence <= 60:
                confidence_lvl = "medium"
            elif 70 <= confidence <= 90:
                confidence_lvl = "high"
            elif confidence == 100:
                confidence_lvl = "highest"
            elif pd.isnull(confidence):
                confidence_lvl = "nan"
            else:
                raise ValueError(f"Bad confidence: {confidence}")
        if ev[2] == EVENTS_ID["confidence"]:
            i_question += 1
        events[i, 2] += confidence_trigger_scores[confidence_lvl]
    return events


def make_epochs(bp_src, bp_annot, bp_dest):
    raw = read_raw_fif(bp_src.fpath)
    if bp_annot.fpath.exists():
        logger.info("Loading annotations from file.")
        raw.set_annotations(read_annotations(bp_annot.fpath))
    events = find_events(raw, min_duration=2 / raw.info["sfreq"])
    events = transform_events(events, "sub-" + bp_dest.subject)
    epochs = Epochs(
        raw,
        events,
        tmin=-1,
        tmax=1,
        baseline=None,
        event_id=ev_id_confidence,
        reject=None,
        flat=None,
        reject_by_annotation=True,
        on_missing="ignore",
    )

    epochs.save(bp_dest.fpath, overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)
    assert args.task not in ("rest", "noise")

    src_bp_ica, src_bp_annot, bp_dest = update_bps(
        [bp_ica, bp_annot_final, bp_epochs],
        subject=args.subject,
        task=args.task,
        session=args.session,
    )
    bp_dest.mkdir(exist_ok=True)

    make_epochs(src_bp_ica, src_bp_annot, bp_dest)
