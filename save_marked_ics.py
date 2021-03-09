from mne.preprocessing import read_ica
from config import subjects, bp_ica_sol, bp_ica_bads, iter_files
from utils import update_bps

for subj, task, _ in iter_files(subjects, runs_return=None):
    src_bp_ica, dest_bp_bads = update_bps(
        [bp_ica_sol, bp_ica_bads], subject=subj, task=task
    )
    ica = read_ica(src_bp_ica.fpath)
    dest_bp_bads.mkdir(exist_ok=True)
    print(dest_bp_bads)
    with open(dest_bp_bads.fpath, "w") as f:
        f.write("\t".join([str(ic) for ic in ica.exclude]))
