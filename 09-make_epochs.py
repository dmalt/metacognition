"""Create epochs from annotated files"""
from argparse import ArgumentParser
from itertools import product

import pandas as pd
import numpy as np

from mne import Epochs, find_events, read_annotations
from mne.io import read_raw_fif

from config import (
    EVENTS_ID,
    bp_ica,
    bp_annot_final,
    bp_epochs,
    bp_beh,
    epochs_config,
    confidence_trigger_scores,
)
from utils import setup_logging
from dataset_specific_utils import get_confidence_level

logger = setup_logging(__file__)

ev_id_confidence = {}
for trig, conf_lvl in product(EVENTS_ID, confidence_trigger_scores):
    ev_id_confidence[trig + "/" + conf_lvl] = (
        EVENTS_ID[trig] + confidence_trigger_scores[conf_lvl]
    )


def get_question_data(i_question, df):
    row = df.loc[i_question]
    try:
        confidence = int(row["оценка"])
    except ValueError:
        confidence = np.nan
    if row["ответ"] in ('1', '2', '3'):
        is_correct = False
    elif row["ответ"] == "c" or row["ответ"] == "с":
        is_correct = True
    else:
        is_correct = np.nan
    try:
        question_num = int(row["question№"])
    except ValueError:
        question_num = np.nan
    return confidence, is_correct, question_num


def transform_events(events, metadata):
    assert len(events[events[:, 2] == EVENTS_ID["answer"]]) == len(metadata)
    assert len(events[events[:, 2] == EVENTS_ID["fixcross"]]) == len(metadata)

    i_question = 0
    for i, ev in enumerate(events):
        if i_question == 0 or ev[2] == EVENTS_ID["question/second"]:
            confidence, is_correct, question_num = get_question_data(
                i_question, beh_df
            )
            confidence_lvl = get_confidence_level(confidence)
        if ev[2] == EVENTS_ID["confidence"]:
            i_question += 1
        beh_data["confidence"].append(confidence)
        beh_data["is_correct"].append(is_correct)
        beh_data["question_num"].append(question_num)
        events[i, 2] += confidence_trigger_scores[confidence_lvl]


def get_events_metadata(events, beh_df):
    """
    Get behavioral metadata for each event

    Since each question corresponds to multiple events, we need to assign
    the same metadata to events within one question. Therefore we pick the next
    question only when the new event is of "confidence" type
    """
    assert len(events[events[:, 2] == EVENTS_ID["answer"]]) == len(beh_df)
    assert len(events[events[:, 2] == EVENTS_ID["fixcross"]]) == len(beh_df)
    i_question = 0
    beh_data = {"confidence": [], "is_correct": [], "question_num": []}
    for i, ev in enumerate(events):
        if i_question == 0 or ev[2] == EVENTS_ID["question/second"]:
            confidence, is_correct, question_num = get_question_data(
                i_question, beh_df
            )
            confidence_lvl = get_confidence_level(confidence)
        if ev[2] == EVENTS_ID["confidence"]:
            i_question += 1
        beh_data["confidence"].append(confidence)
        beh_data["is_correct"].append(is_correct)
        beh_data["question_num"].append(question_num)
        events[i, 2] += confidence_trigger_scores[confidence_lvl]

    metadata = pd.DataFrame(beh_data)
    return events, metadata


def make_epochs(fif_path, annot_path, beh_path, epochs_path):
    raw = read_raw_fif(fif_path)
    if annot_path.exists():
        logger.info("Loading annotations from file.")
        raw.set_annotations(read_annotations(annot_path))
    beh_df = pd.read_csv(beh_path, sep="\t")
    events = find_events(raw, min_duration=2 / raw.info["sfreq"])
    events, metadata = get_events_metadata(events, beh_df)

    epochs = Epochs(
        raw,
        events,
        event_id=ev_id_confidence,
        metadata=metadata,
        **epochs_config
    )
    epochs.save(epochs_path, overwrite=True)


if __name__ == "__main__":
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("subject", help="subject id")
    subj = parser.parse_args().subject

    # input
    cleaned_fif = bp_ica.fpath(subject=subj, task="questions")
    annot = bp_annot_final.fpath(subject=subj, task="questions")
    beh = bp_beh.fpath(subject=subj)
    # output
    epochs = bp_epochs.fpath(subject=subj)

    epochs.parent.mkdir(exist_ok=True, parents=True)

    make_epochs(cleaned_fif, annot, beh, epochs)
