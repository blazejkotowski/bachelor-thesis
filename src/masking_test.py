import numpy as np
import pyaudio
from scipy.io import wavfile
import scipy.signal as signal
from emitter import masking

maskee_f = 8000.0

host_file = "../sounds/carriers/rockvocals.wav"
#host_file = "../sounds/carriers/cello-double.wav"
fs, host = wavfile.read(host_file)
bandstop = signal.firwin(11, [maskee_f - 500, maskee_f + 500], nyq=fs/2)

host = signal.lfilter(bandstop, 1.0, host)
host = host / max(abs(np.array(host, dtype=np.float32)))

space = np.arange(0, len(host))
maskee = np.sin(2*np.pi*maskee_f/fs*space)

out = []
chunk_size = 1024
fftsize = 1024
window = np.hanning(fftsize)
start = 0
last_power = 0

while start + chunk_size < len(host):
  host_chunk = host[start:start+chunk_size]
  maskee_chunk = maskee[start:start+chunk_size]
  power = 0.9 * masking.masking_power(host_chunk, maskee_f, fs)
  if power < 0.01:
    power = 0.01
  print power
  envelope = [ power ] * len(maskee_chunk)
  slope = np.linspace(last_power, power, len(host_chunk) / 2)
  envelope[0:len(slope)] = slope

  out.extend(host_chunk + np.multiply(envelope, maskee_chunk))
  last_power = power
  start += chunk_size


out = out / max(np.abs(out))

pa = pyaudio.PyAudio()
stream = pa.open(format = pyaudio.paFloat32, channels=1, rate=int(fs), output=True)
outpack = np.array(out, dtype=np.float32).tostring()
stream.write(outpack)
