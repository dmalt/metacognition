"""Manually mark bad ICA components and apply solution"""
import sys

from mne.io import read_raw_fif
from mne.preprocessing import read_ica

from config import bp_ica_sol, bp_filt, bp_ica_bads
from utils import setup_logging, parse_args, update_bps

logger = setup_logging(__file__)


def inspect_ica(bp_filt, bp_ica_sol, bp_bads):

    raw = read_raw_fif(bp_filt.fpath, preload=True)
    ica = read_ica(bp_ica_sol.fpath)
    print(bp_bads)
    if bp_bads.fpath.exists():
        with open(bp_bads.fpath, "r") as f:
            line = f.readline()
            if line:
                bads = [int(b) for b in line.split("\t")]
                logger.info(f"Loading BADS from file: {bads}")
            else:
                bads = []
        ica.exclude = bads
    ica.plot_sources(raw, block=True)
    print(ica.info["bads"])
    logger.info(f"Excluding ICs {ica.exclude}")
    with open(bp_bads.fpath, "w") as f:
        f.write("\t".join([str(ic) for ic in ica.exclude]))


if __name__ == "__main__":
    args = parse_args(__doc__, args=sys.argv[1:], is_applied_to_er=True)
    bp_src_filt, bp_src_ica_sol, bp_bads = update_bps(
        [bp_filt, bp_ica_sol, bp_ica_bads],
        subject=args.subject,
        task=args.task,
        session=args.session,
    )
    bp_bads.mkdir(exist_ok=True)
    # logger.info(f"Processing {args.path}")
    # print(f"Processing {args.path}")
    inspect_ica(bp_src_filt, bp_src_ica_sol, bp_bads)
