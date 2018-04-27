import matplotlib.pyplot as plt
import numpy as np

fs = 100
N = 100

sine = np.sin(2*np.pi*10/fs * np.arange(0, N))

x = sine
X = np.fft.fft(x)

magPlot = plt.subplot(211)
magPlot.stem(np.abs(X))
magPlot.set_ylabel('|X|')
magPlot.set_ylim([0, 80])

eps = 0.000001
phase = [ np.angle(Xi) if np.abs(Xi) > eps else 0 for Xi in X]

phasePlot = plt.subplot(212)
phasePlot.plot(phase, '.')
phasePlot.set_ylabel('arg(X)')
phasePlot.set_ylim([-np.pi, np.pi])

#plt.show()
plt.savefig('figures/real-dft.png', transparent=True, dpi=300)
