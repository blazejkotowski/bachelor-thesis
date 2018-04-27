import matplotlib.pyplot as plt
import numpy as np

def ath(f):
  return 3.64*(f/1000.0)**(-0.8) - 6.5*np.exp(-0.6*(f/1000.0-3.3)**2) + 0.001*(f/1000.0)**4

def bark2hz(z):
  return 600 * np.sinh(z/6.0);

plt.figure(figsize=(6, 9))

hertz = np.linspace(0, 20000, 200)
hzPlot = plt.subplot(211)
hzPlot.plot(hertz, ath(hertz))
hzPlot.set_xlabel('frequency [Hz]')
hzPlot.set_ylabel('dB SPL')
hzPlot.set_xlim([0, 20000])
hzPlot.set_ylim([-50, 250])
hzPlot.axhline(y=0, linestyle='--', color='grey')


bark = np.linspace(0, 25, 200)
barkPlot = plt.subplot(212)
barkPlot.plot(bark, ath(bark2hz(bark)))
barkPlot.set_xlabel('frequency [Bark]')
barkPlot.set_ylabel('dB SPL')
barkPlot.set_xlim([0, 25])
barkPlot.axhline(y=0, linestyle='--', color='grey')
barkPlot.set_ylim([-50, 250])

plt.tight_layout()
#plt.show()
plt.savefig('figures/ath.png', transparent=True, dpi=600)
