import math

def goertzel(x, k):
  """Computes spectral component at DFT bin k of signal x"""

  N = len(x) # length of signal
  A = 2*math.pi*k/N
  B = 2*math.cos(A)
  C = math.e ** (-1.0j*A) # e^(-iA)

  s0 = 0
  s1 = 0
  s2 = 0

  for i in range(0, N): # N ranges from 0 ... N - 1
    s0 = x[i] + B * s1 - s2
    s2 = s1
    s1 = s0

  s0 = B * s1 - s2
  return s0 - s1 * C
