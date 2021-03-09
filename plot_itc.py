from mne.time_frequency import read_tfrs
from config import subjects, bp_itc, bp_tfr


for subj in subjects:
    itc_path_low = bp_tfr.fpath(subject=subj, task="low")
    itc_path_high = bp_tfr.fpath(subject=subj, task="high")

    itc_low = read_tfrs(itc_path_low)[0]
    itc_high = read_tfrs(itc_path_high)[0]
    (itc_high - itc_low).plot_topo()
    # itc_low.plot_topo()
