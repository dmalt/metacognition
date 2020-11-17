from mne_bids import make_dataset_description
from config import BIDS_ROOT, DATASET_NAME, AUTHORS, subj_ids_file, RAW_DIR
from utils import SubjectRenamer

# DOIT_CONFIG = {
#     "default_tasks": [
#         "prepare_bids",
#         "make_dataset_description",
#         "register_subjects",
#     ]
# }


def task_register_subjects():
    """
    Register subject

    Add subject name subj_ids_file and assign it a numerical
    index depending on its measurement date

    """
    return dict(
        file_dep=["register_subjects.py"],
        targets=[subj_ids_file],
        actions=["python register_subjects.py"],
    )


def task_prepare_bids():
    """Copy new subjects from raw folder to BIDS folders structure"""
    renamer = SubjectRenamer(subj_ids_file)
    for subject in renamer.subj_ids_map:
        yield {
            "name": f"{subject}",
            "actions": [f"python 00-prepare_bids.py {subject}"],
            "targets": [f"{BIDS_ROOT / renamer.subj_ids_map[subject]}"],
        }


def task_make_dataset_description():
    """Create dataset_description.json"""
    return {
        "actions": [
            (
                make_dataset_description,
                [],
                {
                    "path": BIDS_ROOT,
                    "name": DATASET_NAME,
                    "authors": AUTHORS,
                    "overwrite": True,
                },
            )
        ],
        "targets": ["dataset_description.json"],
    }
