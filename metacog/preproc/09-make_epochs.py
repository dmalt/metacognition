"""
Create epochs

Remove bad segments based on annotations.
Add metadata from behavioral answers if provided.

"""
from argparse import ArgumentParser

import pandas as pd

from mne import Epochs, find_events, read_annotations
from mne.io import read_raw_fif

from metacog import bp
from metacog.config import EVENTS_ID, tasks, epochs_config
from metacog.utils import setup_logging
from metacog.dataset_specific_utils import get_events_metadata

logger = setup_logging(__file__)


def make_epochs(fif_path, annot_path, beh_path, ep_path):
    raw = read_raw_fif(fif_path)
    if annot_path.exists():
        logger.info("Loading annotations from file.")
        raw.set_annotations(read_annotations(annot_path))
    events = find_events(raw, min_duration=2 / raw.info["sfreq"])

    if beh_path:
        beh_df = pd.read_csv(beh_path, sep="\t")
        metadata = get_events_metadata(events, beh_df)
    else:
        metadata = None

    epochs = Epochs(
        raw, events, event_id=EVENTS_ID, metadata=metadata, **epochs_config
    )
    epochs.save(ep_path, overwrite=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("subject", help="subject id")
    subj = parser.parse_args().subject

    # input
    cleaned_fif = bp.ica.fpath(subject=subj, task=tasks[0])
    annot = bp.annot_final.fpath(subject=subj, task=tasks[0])
    beh = bp.beh.fpath(subject=subj)
    # output
    epochs = bp.epochs.fpath(subject=subj)

    epochs.parent.mkdir(exist_ok=True, parents=True)

    make_epochs(cleaned_fif, annot, beh, epochs)
