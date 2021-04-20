from metacog.paths import dirs
from metacog.utils import BIDSPathTemplate
from metacog.config import fwd_config, tasks


root = BIDSPathTemplate(
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# only need this to get emptyroom, so no session template
root_json = BIDSPathTemplate(
    root=dirs.bids_root, datatype="meg", suffix="meg", extension=".json",
    template_vars=["subject", "task", "run"],
)
# ------------------------- 01-compute_head_position ------------------------ #
headpos = BIDSPathTemplate(
    root=dirs.hp, suffix="hp", extension=".pos",
    template_vars=["subject", "task", "run"],
)
# --------------------------------------------------------------------------- #

# ------------------------- 02-mark_bads_maxfilter -------------------------- #
annot = BIDSPathTemplate(
    root=dirs.bads, suffix="annot", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
bads = annot.update(suffix="bads", extension="tsv")
# --------------------------------------------------------------------------- #

# ---------------------------- 03-apply_maxfilter --------------------------- #
maxfilt = BIDSPathTemplate(
    root=dirs.maxfilter, processing="sss", suffix="meg", extension=".fif",
    template_vars=["subject", "task", "run", "session"],
)
# --------------------------------------------------------------------------- #

# ------------------------ 04-concat_filter_resample ------------------------ #
filt = BIDSPathTemplate(
    root=dirs.filter, processing="filt", suffix="meg", extension="fif",
    template_vars=["subject", "task", "session"],
)
# --------------------------------------------------------------------------- #

# ------------------------------ 05-compute_ica ----------------------------- #
ica_sol = BIDSPathTemplate(
    root=dirs.ica_sol, processing="filt", suffix="ica", extension=".fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ----------------------------- 06-inspect_ica ------------------------------ #
ica_bads = BIDSPathTemplate(
    root=dirs.ica_bads, processing="filt", suffix="icabads", extension="tsv",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ------------------------------- 07-apply_ica ------------------------------ #
ica = BIDSPathTemplate(
    root=dirs.ica, processing="ica", suffix="meg", extension="fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# --------------------------- 08-mark_bad_segments -------------------------- #
annot_final = BIDSPathTemplate(
    root=dirs.bad_segments, processing="ica", suffix="annot", extension="fif",
    template_vars=["subject", "task"],
)
# --------------------------------------------------------------------------- #

# ------------------------------ 09-make_epochs ----------------------------- #
epochs = BIDSPathTemplate(
    root=dirs.epochs, processing="ica", task=tasks[0], suffix="epo", extension="fif", # noqa
    template_vars=["subject"],
)
beh = BIDSPathTemplate(
    root=dirs.bids_root, datatype="beh", task=tasks[0], suffix="behav", extension="tsv", # noqa
    template_vars=["subject"]
)
# --------------------------------------------------------------------------- #

# ----------------------------------- FSF ----------------------------------- #
anat = BIDSPathTemplate(
    root=dirs.bids_root, datatype="anat", suffix="T1w", extension="nii.gz",
    template_vars=["subject"],
)
# --------------------------------------------------------------------------- #

# -------------------------------- 10-coreg --------------------------------- #
trans = BIDSPathTemplate(
    root=dirs.coreg, suffix="trans", extension="fif",
    template_vars=["subject"],
)
# --------------------------------------------------------------------------- #

# --------------------------- 11-compute_forward ---------------------------- #
fwd = BIDSPathTemplate(
    root=dirs.forwards, acquisition=fwd_config["spacing"], suffix="fwd", extension="fif", # noqa
    template_vars=["subject"]
)
# --------------------------------------------------------------------------- #

# ---------------------------- 12-compute_inverse --------------------------- #
inv = BIDSPathTemplate(
    root=dirs.inverse, suffix="inv", acquisition=fwd_config["spacing"], extension="fif", # noqa
    template_vars=["subject"],
)

# --------------------------------------------------------------------------- #

# -------------------------- 15-compute_tfr_epochs -------------------------- #
tfr = BIDSPathTemplate(
    root=dirs.tfr, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject"],
)
# itc = BIDSPathTemplate(
#     root=dirs.tfr, processing="ica", suffix="itc", extension="h5", # noqa
#     template_vars=["subject"],
# )
# --------------------------------------------------------------------------- #

# ------------------------------- average_tfr ------------------------------- #
tfr_av = BIDSPathTemplate(
    root=dirs.tfr_average, processing="ica", suffix="tfr", extension="h5", # noqa
    template_vars=["subject", "acquisition"],
)
# --------------------------------------------------------------------------- #
