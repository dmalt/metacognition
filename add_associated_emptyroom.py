"""Add associated emptyroom paths to sidecar json files"""
import sys
import json

from config import bp_root_json, bp_root, BIDS_ROOT
from dataset_specific_utils import parse_args
from utils import setup_logging

logger = setup_logging(__file__)

args = parse_args(__doc__, sys.argv[1:], emptyroom=False)
subj, task, run = args.subject, args.task, args.run

json_path = bp_root_json.fpath(subject=subj, task=task, run=run)
raw_bp = bp_root.update(subject=subj, task=task, run=run, session=None)
logger.info(f"Reading json from {json_path}")
with open(json_path, "r") as f:
    json_dict = json.load(f)

bp_er = raw_bp.find_empty_room()
associated_er_path = bp_er.fpath.relative_to(BIDS_ROOT)
logger.info(f"Setting AssociatedEmptyRoom to {associated_er_path}")
json_dict["AssociatedEmptyRoom"] = str(associated_er_path)


logger.info(f"Writing json back to {json_path}")
with open(json_path, "w") as f:
    json.dump(json_dict, f, indent=4)
