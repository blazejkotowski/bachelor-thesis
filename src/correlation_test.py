import numpy as np
import matplotlib.pyplot as plt
import random

fs = 44100
N = fs
f = 5000
chunk = 256
shift = (random.random() * 2 - 1) * np.pi
sine1 = np.sin([ 2*np.pi*f*n/fs + shift for n in range(0, N)])
sine2 = np.sin([ 2*np.pi*f*n/fs for n in range(0, N)])

plt.show()

corr = np.correlate(sine1[:chunk], sine2[:chunk/4])

plt.plot(sine1[:chunk])
plt.plot(sine2[:chunk/2])
plt.plot(corr)
# plt.show()

corr_idx = np.argmax(corr)
sample_per_period = float(fs) / f
period_shift = corr_idx / sample_per_period
phase_shift = (1-(period_shift % 1.0)) * (2*np.pi)

if phase_shift > np.pi:
  phase_shift -= 2*np.pi

print corr_idx, sample_per_period, period_shift
print "shift: {0}, err: {1}".format(phase_shift, abs(shift - phase_shift))
