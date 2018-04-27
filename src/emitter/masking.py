import numpy as np
import scipy.signal as signal

def hz2bark(f):
  return 13*np.arctan(0.00076*f) + 3.5*np.arctan((f/7500.0)**2)

def mag2db(x):
  return 10*np.log10(x)

def db2mag(mag):
  return 10**(0.1*mag)

def hz2bin(f, fs, fftsize):
  return np.round((2.0 * f / fs) * (fftsize / 2.0))

def bin2hz(idx, fs, fftsize):
  return (float(idx) / fftsize) * fs

def spreading(p, bark_i, bark_j):
  d_bark = bark_i - bark_j
  if -3.0 <= d_bark < -1.0:
    return 17.0 * d_bark - 0.4 * p + 11
  elif -1.0 <= d_bark < 0.0:
    return (0.4 * p + 6) * d_bark
  elif 0.0 <= d_bark < 1.0:
    return -17.0 * d_bark
  elif 1.0 <= d_bark < 8:
    return (0.15 * p - 17.0) * d_bark - 0.15 * p
  else:
    return False

def masking_power(x, maskee_f, fs):
  fftsize = len(x)
  window = np.hanning(fftsize)

  X = np.abs(np.fft.rfft(x * window))
  P = mag2db(X**2)

  tones = [ False ] * len(P)
  for idx, p in enumerate(P):
    if idx == 0 or idx == len(P)-1:
      continue
    if P[idx-1] < p and P[idx+1] < p:
      if bin2hz(idx, fs, fftsize) < 5500.0:
        neighbourhood = 2
      elif bin2hz(idx, fs, fftsize) < 11000.0:
        neighbourhood = 3
      else:
        neighbourhood = 6
      neighbourhood_p = list(P[idx-neighbourhood:idx-1]) + list(P[idx+2:idx+neighbourhood+1])
      if all([ True if neighbour == p else neighbour < p - 7.0 for neighbour in neighbourhood_p ]):
        tones[idx-neighbourhood:idx+neighbourhood+1] = [ True ] * len(tones[idx-neighbourhood:idx+neighbourhood+1])
        tones[idx] = mag2db(db2mag(P[idx-1]) + db2mag(P[idx]) + db2mag(P[idx+1]))

  ath = 3.64*(maskee_f/1000.0)**(-0.8) - 6.5*np.exp(-0.6*(maskee_f/1000.0-3.3)**2) + 0.001*(maskee_f/1000.0)**4
  threshold = db2mag(ath)
  for idx, p in enumerate(tones):
    if type(p) == np.float64:
      bark_i = hz2bark(maskee_f)
      bark_j = hz2bark(bin2hz(idx, fs, fftsize))
      spr = spreading(p, bark_i, bark_j)
      if spr:
        threshold += db2mag(p - 0.275 * bark_j + spr + 6.025)
  return (threshold / fftsize)
