from pathlib import Path
from types import SimpleNamespace

from metacog.utils import BIDSPathTemplate
from metacog.config import BIDS_ROOT, tasks, fwd_config


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
dirs.subjects     = dirs.derivatives / "FSF"                        # noqa
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
subj_ids_file = dirs.bids_root / "code" / "added_subjects.tsv"
# --------------------------------------------------------------------------- #

bp_root = BIDSPathTemplate(
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# only need this to get emptyroom, so no session template
bp_root_json = BIDSPathTemplate(
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".json",
    template_vars=["subject", "task", "run"],
)
# ------------------------- 01-compute_head_position ------------------------ #
bp_headpos = BIDSPathTemplate(
    root=dirs.hp, suffix="hp", extension=".pos",
    template_vars=["subject", "task", "run"],
)
# --------------------------------------------------------------------------- #

# ------------------------- 02-mark_bads_maxfilter -------------------------- #
bp_annot = BIDSPathTemplate(
    root=dirs.bads, suffix="annot", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
bp_bads = bp_annot.update(suffix="bads", extension="tsv")
# --------------------------------------------------------------------------- #

# ---------------------------- 03-apply_maxfilter --------------------------- #
bp_maxfilt = BIDSPathTemplate(
    root=dirs.maxfilter, processing="sss", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# --------------------------------------------------------------------------- #

# ------------------------ 04-concat_filter_resample ------------------------ #
bp_filt = BIDSPathTemplate(
    root=dirs.filter, processing="filt", suffix="meg", extension="fif",
    template_vars=["subject", "task", "session"],
)
# --------------------------------------------------------------------------- #

# ------------------------------ 05-compute_ica ----------------------------- #
bp_ica_sol = BIDSPathTemplate(
    root=dirs.ica_sol, processing="filt", suffix="ica", extension=".fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ----------------------------- 06-inspect_ica ------------------------------ #
bp_ica_bads = BIDSPathTemplate(
    root=dirs.ica_bads, processing="filt", suffix="icabads", extension="tsv",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ------------------------------- 07-apply_ica ------------------------------ #
bp_ica = BIDSPathTemplate(
    root=dirs.ica, processing="ica", suffix="meg", extension="fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# --------------------------- 08-mark_bad_segments -------------------------- #
bp_annot_final = BIDSPathTemplate(
    root=dirs.bad_segments, processing="ica", suffix="annot", extension="fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ------------------------------ 09-make_epochs ----------------------------- #
bp_epochs = BIDSPathTemplate(
    root=dirs.epochs, processing="ica", task=tasks[0], suffix="epo", extension="fif", # noqa
    template_vars=["subject"],
)
bp_beh = BIDSPathTemplate(
    root=dirs.bids_root, datatype="beh", task=tasks[0], suffix="behav", extension="tsv", # noqa
    template_vars=["subject"]
)
# --------------------------------------------------------------------------- #

# ----------------------------------- FSF ----------------------------------- #
bp_anat = BIDSPathTemplate(
    root=dirs.bids_root, datatype="anat", suffix="T1w", extension="nii.gz",
    template_vars=["subject"],
)
# --------------------------------------------------------------------------- #

# -------------------------------- 10-coreg --------------------------------- #
bp_trans = BIDSPathTemplate(
    root=dirs.coreg, suffix="trans", extension="fif",
    template_vars=["subject"],
)
# --------------------------------------------------------------------------- #

# --------------------------- 11-compute_forward ---------------------------- #
bp_fwd = BIDSPathTemplate(
    root=dirs.forwards, acquisition=fwd_config["spacing"], suffix="fwd", extension="fif", # noqa
    template_vars=["subject"]
)
# --------------------------------------------------------------------------- #

# ---------------------------- 12-compute_inverse --------------------------- #
bp_inv = BIDSPathTemplate(
    root=dirs.inverse, suffix="inv", acquisition=fwd_config["spacing"], extension="fif", # noqa
    template_vars=["subject"],
)

# --------------------------------------------------------------------------- #

# -------------------------- 15-compute_tfr_epochs -------------------------- #
bp_tfr = BIDSPathTemplate(
    root=dirs.tfr, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject"],
)
# bp_itc = BIDSPathTemplate(
#     root=dirs.tfr, processing="ica", suffix="itc", extension="h5", # noqa
#     template_vars=["subject"],
# )
tfr_config = dict(
    freqs=dict(start=1.0, stop=30., step=1.),
    decim=4,
    use_fft=True,
)
# --------------------------------------------------------------------------- #

# ------------------------------- average_tfr ------------------------------- #
bp_tfr_av = BIDSPathTemplate(
    root=dirs.tfr_average, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject", "acquisition"],
)
# --------------------------------------------------------------------------- #


if __name__ == "__main__":
    for k, d in vars(dirs).items():
        print(k, d, sep=":")
