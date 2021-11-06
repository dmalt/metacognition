from pathlib import Path
from types import SimpleNamespace

from metacog.config_parser import get_config
BIDS_ROOT = get_config().BIDS_ROOT


# ---------------------------- setup directories ---------------------------- #
dirs = SimpleNamespace()

dirs.current = Path(__file__).resolve().parent
dirs.bids_root = Path(BIDS_ROOT)

dirs.raw          = dirs.bids_root.parent / "raw"                   # noqa
dirs.beh_raw      = dirs.raw / "behavioral_data"                    # noqa
dirs.logs         = dirs.current / "logs"                           # noqa

dirs.derivatives  = dirs.bids_root   / "derivatives"                # noqa
dirs.hp           = dirs.derivatives / "01-head_positon"            # noqa
dirs.bads         = dirs.derivatives / "02-maxfilter_bads"          # noqa
dirs.maxfilter    = dirs.derivatives / "03-maxfilter"               # noqa
dirs.filter       = dirs.derivatives / "04-concat_filter_resample"  # noqa
dirs.ica_sol      = dirs.derivatives / "05-compute_ica"             # noqa
dirs.ica_bads     = dirs.derivatives / "06-inspect_ica"             # noqa
dirs.ica          = dirs.derivatives / "07-apply_ica"               # noqa
dirs.bad_segments = dirs.derivatives / "08-mark_bad_segments"       # noqa
dirs.epochs       = dirs.derivatives / "09-make_epochs"             # noqa
dirs.fsf_subjects = dirs.derivatives / "FSF"                        # noqa
dirs.coreg        = dirs.derivatives / "10-coreg"                   # noqa
dirs.forwards     = dirs.derivatives / "11-forwards"                # noqa
dirs.inverse      = dirs.derivatives / "12-inverses"                # noqa
dirs.sources      = dirs.derivatives / "13-sources"                 # noqa
dirs.tfr          = dirs.derivatives / "15-tfr"                     # noqa
dirs.tfr_average  = dirs.derivatives / "16-average_tfr"             # noqa
dirs.reports      = dirs.derivatives / "99-reports"                 # noqa

# create directories for derivatives
for k, d in vars(dirs).items():
    if k not in ("raw", "beh_raw", "bids_root"):
        d.mkdir(exist_ok=True, parents=True)

crosstalk_file = str(dirs.bids_root / "SSS_data" / "ct_sparse.fif")
cal_file = str(dirs.bids_root / "SSS_data" / "sss_cal.dat")
# --------------------------------------------------------------------------- #


if __name__ == "__main__":
    for k, d in vars(dirs).items():
        print(k, d, sep=":")
