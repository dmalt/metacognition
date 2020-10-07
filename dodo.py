from mne_bids import make_dataset_description
from config import BIDS_ROOT, DATASET_NAME, AUTHORS


def task_make_dataset_description():
    return {
        "actions": [
            (
                make_dataset_description,
                [],
                {"path": BIDS_ROOT, "name": DATASET_NAME, "authors": AUTHORS},
            )
        ]
    }
