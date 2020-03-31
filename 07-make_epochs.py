from operator import attrgetter
from itertools import product

import pandas as pd
import numpy as np

from mne import Epochs, find_events, read_epochs
from mne.io import read_raw_fif

from config import BIDS_ROOT, ICA_DIR, EPOCHS_DIR, ev_id
from utils import output_log, BidsFname

output_log(__file__)

confidence_trigger_scores = {
    "lowest": 10,
    "low": 20,
    "medium": 30,
    "high": 40,
    "highest": 50,
    "nan": 60,
}

ev_id_confidence = {}
for trig, conf_lvl in product(ev_id, confidence_trigger_scores):
    ev_id_confidence[trig + "/" + conf_lvl] = (
        ev_id[trig] + confidence_trigger_scores[conf_lvl]
    )


def transform_events(events, subj_name):

    beh_fpath = next((BIDS_ROOT / subj_name / "beh").glob("*.tsv"))
    beh_df = pd.read_csv(beh_fpath, sep="\t")
    assert len(events[events[:, 2] == ev_id["answer"]]) == len(beh_df)
    assert len(events[events[:, 2] == ev_id["fixcross"]]) == len(beh_df)

    i_question = 0
    for i, ev in enumerate(events):
        if i_question == 0 or ev[2] == ev_id["question/second"]:
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
        if ev[2] == ev_id["confidence"]:
            i_question += 1
        events[i, 2] += confidence_trigger_scores[confidence_lvl]
    return events


def make_epochs(fif_file):
    bids_fname = BidsFname(fif_file.name)
    subj_name = bids_fname.to_string("sub")
    dist_dir = EPOCHS_DIR / subj_name
    dist_dir.mkdir(exist_ok=True)
    savepath = dist_dir / (bids_fname.base + "-epo.fif")
    if savepath.is_file():
        epochs = read_epochs(str(savepath))
    else:
        raw = read_raw_fif(str(fif_file))
        if bids_fname["task"] == "rest":
            pass
        else:
            events = find_events(raw, min_duration=2 / raw.info["sfreq"])
            events = transform_events(events, subj_name)
            epochs = Epochs(
                raw,
                events,
                tmin=-1,
                tmax=1,
                baseline=None,
                event_id=ev_id_confidence,
                reject=None,
                flat=None,
                on_missing="ignore",
            )
    epochs.plot(block=True)

    epochs.save(str(savepath), overwrite=True)


if __name__ == "__main__":
    fif_files = sorted(
        list(ICA_DIR.rglob("*task-questions*ica_meg.fif")),
        key=attrgetter("name"),
    )
    for fif_file in fif_files:
        print(f"Processing {fif_file.name}")
        make_epochs(fif_file)
