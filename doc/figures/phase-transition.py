import matplotlib.pyplot as plt
import numpy as np

# pi phase transition

sine1 = np.cos(np.linspace(-4*np.pi, 0, endpoint=False))
sine2 = np.cos(np.linspace(np.pi, 5*np.pi))
sines = np.concatenate((sine1, sine2))

plt.figure(figsize=(9, 3))
plt.ylim([-1.2, 1.2])
plt.xticks([])
plt.yticks([])
plt.ylabel('amplitude')
plt.xlabel('time')
plt.plot(sines)

#plt.show()
plt.savefig('figures/phase-transition.png', transparent=True, dpi=300)
