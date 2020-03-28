from mne.io import read_raw_fif
from mne.preprocessing import read_ica

from config import ICA_SOL_DIR, ICA_DIR, FILTER_DIR
from utils import BidsFname, output_log
import sys

output_log(__file__)


def exclude_ics_and_apply(fif_file):
    bids_fname = BidsFname(fif_file.name)
    subjname = bids_fname.to_string("sub")

    raw = read_raw_fif(str(fif_file), preload=True)
    ica_fpath = ICA_SOL_DIR / subjname / (bids_fname.base + "-ica.fif")
    ica = read_ica(str(ica_fpath))
    ica.plot_sources(raw, block=True)
    while True:
        ans = input("continue? (y/n/number)").upper()
        if ans == "Y":
            break
        elif ans == "N":
            sys.exit()
        try:
            n = int(ans)
            try:
                ica.plot_properties(raw, psd_args={"fmax": 50}, picks=n)
            except Exception:
                pass
        except ValueError:
            pass
        print(f"Excluding ICs {ica.exclude}")
    ica.save(str(ica_fpath))
    ica.apply(raw)

    dest_raw_dir = ICA_DIR / subjname
    dest_raw_dir.mkdir(exist_ok=True)
    bids_fname["proc"] = "ica"
    dest_raw_fpath = dest_raw_dir / str(bids_fname)
    raw.save(dest_raw_fpath, overwrite=True)


if __name__ == "__main__":
    fif_files = FILTER_DIR.rglob("sub-[0-9][1-9]*_meg.fif")
    for f in fif_files:
        print(f"Processing {f.name}")
        exclude_ics_and_apply(f)
