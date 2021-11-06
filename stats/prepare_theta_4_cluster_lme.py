from metacog.group_analysis.reproduce_wynn.utils import prepare_band_power
from metacog.dataset_specific_utils import assemble_epochs_new
import numpy as np
import pickle

freq_band = (4, 8)
time_win = (0.4, 0.8)
ch_group = "parietal"
psd_params = dict(fmin=0, fmax=30, n_fft=128)
ch_type = "grad"

X, meta, times, info = assemble_epochs_new(ch_type=ch_type)
df, power, freqs = prepare_band_power(
    times, time_win, meta, X, freq_band, info, psd_params
)

np.save("theta_power.npy", power)

with open("theta_power_regressors.pkl", "wb") as f:
    pickle.dump(df, f)
