import matplotlib.pyplot as plt
import numpy as np

# smoothed pi phase transition

sine1 = np.cos(np.linspace(-4*np.pi, 0, endpoint=False))
sine2 = np.cos(np.linspace(np.pi, 5*np.pi))
sines = np.concatenate((sine1, sine2))

wsize = 26
padding = np.ones((len(sines)-wsize) / 2)
window = np.concatenate((padding, (1 - np.cos(np.linspace(-np.pi, np.pi, wsize))) / 2.0, padding))
plt.figure(figsize=(9, 3))
plt.ylim([-1.2, 1.2])
plt.xticks([])
plt.yticks([])
plt.ylabel('amplitude')
plt.xlabel('time')
plt.plot(np.multiply(sines, window))

#plt.show()
plt.savefig('figures/smooth-phase-transition.png', transparent=True, dpi=300)
