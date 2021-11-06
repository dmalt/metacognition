from mne.time_frequency import read_tfrs
from config import subjects, bp_epochs, bp_tfr, bp_tfr_av
band = "alphabeta"
for subj in subjects:
    print(subj)
    tfr_path = bp_tfr_av.fpath(subject=subj, acquisition=band)
    tfr = read_tfrs(tfr_path)[0]["confidence < 100 and confidence > 0"]
    # tfr = read_tfrs(tfr_path)[0]
    df = tfr.metadata.copy()
    df["subject"] = subj

