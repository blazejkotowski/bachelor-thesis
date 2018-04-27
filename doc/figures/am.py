import matplotlib.pyplot as plt
import numpy as np
import scipy.signal as signal
import random

fs = 10000
N = fs

s1 = np.sin(2*np.pi*1/fs * np.arange(0, N))
s2 = s1 * np.sin(2*np.pi*20/fs * np.arange(0, N))

plot1 = plt.subplot(211)
plot1.plot(s1)
plot1.set_xlabel('time')
plot1.set_xticks([])

plot2 = plt.subplot(212)
plot2.plot(s2)
plot2.set_xlabel('time')
plot2.set_xticks([])

plt.tight_layout()
# plt.show()
plt.savefig('figures/am.png', transparent=True, dpi=600)
