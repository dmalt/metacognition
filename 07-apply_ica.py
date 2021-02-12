"""Manually mark bad ICA components and apply solution"""
import sys

from mne.io import read_raw_fif
from mne.preprocessing import read_ica

from config import bp_ica_sol, bp_filt, bp_ica, bp_ica_bads
from utils import setup_logging, parse_args, update_bps

logger = setup_logging(__file__)


def exclude_ics_and_apply(bp_filt, bp_ica_sol, bp_bads, bp_dest):
    raw = read_raw_fif(str(bp_filt.fpath), preload=True)
    ica = read_ica(str(bp_ica_sol.fpath))
    with open(bp_bads.fpath, "r") as f:
        line = f.readline()
        if line:
            bads = [int(b) for b in line.split("\t")]
            logger.info(f"Loading BADS from file: {bads}")
        else:
            bads = []
    ica.exclude = bads
    logger.info(f"Excluding ICs {ica.exclude}")
    ica.apply(raw)
    raw.save(str(bp_dest.fpath), overwrite=True)


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)
    bp_src_filt, bp_src_ica_sol, bp_src_bads, bp_dest = update_bps(
        [bp_filt, bp_ica_sol, bp_ica_bads, bp_ica],
        subject=args.subject,
        task=args.task,
        session=args.session,
    )
    bp_dest.mkdir(exist_ok=True)
    # logger.info(f"Processing {args.path}")
    # print(f"Processing {args.path}")
    exclude_ics_and_apply(bp_src_filt, bp_src_ica_sol, bp_src_bads, bp_dest)
