import numpy as np

def goertzel(x, k):
  N = len(x)
  A = 2*np.pi*k/N
  B = 2*np.cos(A)
  C = np.exp(-1j*A)
  D = np.exp(-1j*(2*np.pi*k/N)*(N-1))
  s0 = 0
  s1 = 0
  s2 = 0
  for i in range(0, N-1):
    s0 = x[i] + B*s1 - s2
    s2 = s1
    s1 = s0
  s0 = x[N-1] + B*s1 - s2
  y = s0 - s1*C
  return y*D
