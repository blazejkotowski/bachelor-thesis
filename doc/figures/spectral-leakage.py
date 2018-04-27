import matplotlib.pyplot as plt
import numpy as np

fs = 100
N = 50

sine1 = np.sin(2*np.pi*25/fs * np.arange(0, N))
sine2 = np.sin(2*np.pi*24/fs * np.arange(0, N))

X1 = np.fft.rfft(sine1)
X2 = np.fft.rfft(sine2)

plt.figure(figsize=(8, 5))

sine10Plot = plt.subplot(211)
sine10Plot.stem(np.abs(X1))
sine10Plot.set_ylabel('|X|')
sine10Plot.set_ylim([0, 30])

sine11Plot = plt.subplot(212)
sine11Plot.stem(np.abs(X2))
sine11Plot.set_ylabel('|X|')
sine11Plot.set_ylim([0, 30])

# plt.show()
plt.savefig('figures/spectral-leakage.png', transparent=True, dpi=300)
