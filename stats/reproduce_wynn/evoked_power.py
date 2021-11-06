"""
Evoked power analysis

NOTE
----
In the paper (Wynn 2019) they seem not to care about different number of trials
in different conditions when computing the evoked response

"""
import statsmodels.formula.api as smf
import matplotlib.pyplot as plt
import numpy as np
from mne.time_frequency import psd_array_welch

from metacog.dataset_specific_utils import assemble_epochs_new
from metacog.group_analysis.reproduce_wynn.utils import prepare_erp

time_window = (0.4, 0.8)
ch_group = "parietal"
ch_type = "grad"
freq_band = (4, 8)
baseline = (-0.2, 0)

X, meta, times, info = assemble_epochs_new(ch_type=ch_type, baseline=baseline)

df, data = prepare_erp(times, time_window, ch_group, meta, X, info)

psd_params = dict(fmin=0, fmax=30, n_fft=128)

time_mask = np.logical_and(times >= time_window[0], times < time_window[1])
psd, freqs = psd_array_welch(
    data[:, :, time_mask], sfreq=info["sfreq"], **psd_params
)
freq_mask = np.logical_and(freqs >= freq_band[0], freqs < freq_band[1])
df.data = psd[:, :, freq_mask].mean(axis=(1, 2)) * 1e13 ** 2

md = smf.mixedlm("data ~ cond", data=df, groups="subj")
mdf = md.fit()
print(mdf.summary())


legend = []
for cond in np.unique(df.cond):
    plt.plot(freqs, psd[df.cond == cond, :, :].mean(axis=(0, 1)))
    legend.append(cond)
plt.legend(legend)
plt.show()
