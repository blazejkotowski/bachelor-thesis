import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import random

fs = 44100
N = fs

noise = [ random.random() for i in range(N) ]
bandpass = signal.firwin(100, [ 8000.0, 12000.0 ], pass_zero=False, nyq=fs/2)
filtered_noise = signal.lfilter(bandpass, 1.0, noise)

X1 = np.fft.rfft(noise)
X2 = np.fft.rfft(filtered_noise)

origPlot = plt.subplot(211)
origPlot.plot(np.abs(X1))
origPlot.set_xlabel('frequency [Hz]')
origPlot.set_ylabel('|X|')
origPlot.set_ylim([0, 250])
origPlot.set_xlim([0, N/2])

filterPlot = plt.subplot(212)
filterPlot.plot(np.abs(X2))
filterPlot.set_xlabel('frequency [Hz]')
filterPlot.set_ylabel('|X|')
filterPlot.set_ylim([0, 250])
filterPlot.set_xlim([0, N/2])

plt.tight_layout()
#plt.show()
plt.savefig('figures/bandpass-filter.png', transparent=True, dpi=600)
