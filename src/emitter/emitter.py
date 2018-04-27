import numpy as np
import scipy.signal as signal
import random
import copy
import sys
from encoding import Encoder
from masking import masking_power

import matplotlib.pyplot as plt

def debug(message):
  sys.stderr.write(str(message))

class Emitter:
  """ Given carrier signal, payload data, and configuration parameters,
      this class synthesizes output signal with hidden payload data
  """
  def __init__(self, host, sample_rate, sync_frequency, carrier_frequencies, payload):
    """ Constructor method

    Keyword arguments:
    host -- one-dimensional array of host signal
    sample_rate -- sampling rate to be used for analysis/synthesis
    sync_frequency -- configurable frequency of sync signal, in Hz
    carrier_frequencies -- configurable frequencies of carrier signals, array of 8 elements, in Hz
    payload -- data to be hidden in output signal, array of bytes (int)
    """

    low_freq = min(sync_frequency, min(carrier_frequencies)) - 100
    high_freq = max(sync_frequency, max(carrier_frequencies)) + 100
    bandstop = signal.firwin(1001, [low_freq, high_freq], nyq=sample_rate/2)
    self.host = host
    self.filtered_host = signal.lfilter(bandstop, 1.0, host)
    self.host /= max(self.host)
    self.filtered_host /= max(self.filtered_host)
    self.sample_rate = sample_rate
    self.payload = payload
    self.sync_frequency = sync_frequency
    self.carrier_frequencies = carrier_frequencies
    self.byte_duration = 0.2
    self.byte_buffer_size = int(self.sample_rate * self.byte_duration)
    self.host_index = 0
    self.byte_window = self.__get_byte_window()

    debug("> sync frequency: {0} Hz\n".format(self.sync_frequency))
    debug("> carrier frequencies: {0}\n".format(self.carrier_frequencies))

  def outstream(self, buf):
    """ Synthesize output stream, using DBPSK modulation of carrier signals

    Chunks of synthesized signal will be put on an output queue.
    When output stream is finished, False is put on queue.

    Keyword arguments:
    buf -- an output Queue
    """

    # Send 0b00 byte, for differential encoding phase reference
    shifts = np.zeros(8, dtype=np.int8)
    (shifts, samples) = self.__encode_byte(shifts, 0b00, -1)
    buf.put(samples)

    bts = Encoder(self.payload).encode() + [0b00]
    for byteidx, byte in enumerate(bts):
      # Simulate random errors
      # if (byteidx%24) < 2:
      #   malform = random.randint(0, 8)
      #   byte = byte | 2**malform
      # if random.randint(1, 20) == 1:
      #   byte = random.randint(0, 254)
      (shifts, samples) = self.__encode_byte(shifts, byte, byteidx)
      buf.put(samples)
    buf.put(False)
    return buf

  def __encode_byte(self, last_shifts, byte, byteidx):
    """ Encode a single byte using last phase shifts

    Differential Binary Phase Shift Keying:
    - no phase shift encodes 0
    - phase shift of pi encodes 1
    """

    byterange = range(0, 8)
    shifts = [ (last_shifts[i] + 1) % 2 if (byte >> i) & 0b01 == 1 else last_shifts[i] for i in byterange ]

    samples_start = byteidx*self.byte_buffer_size
    samples_end = samples_start + self.byte_buffer_size
    samples_range = (samples_start, samples_end)

    sync_signal = self.__sine(samples_range, self.sync_frequency, (byteidx % 2) * np.pi)
    carrier_signals = [ self.__sine(samples_range, frequency, shifts[carrier_idx] * np.pi) for carrier_idx, frequency in enumerate(self.carrier_frequencies) ]
    buf = np.sum(carrier_signals + [sync_signal], axis=0) / (len(byterange) + 1)

    filtered_carrier = self.filtered_host[self.host_index:self.host_index+len(buf)]
    carrier = self.host[self.host_index:self.host_index+len(buf)]

    if len(carrier) < len(buf):
      remainder_index = len(buf) - len(carrier)
      filtered_carrier = np.append(filtered_carrier, self.filtered_host[0:remainder_index])
      carrier = np.append(carrier, self.filtered_host[0:remainder_index])
      self.host_index = remainder_index + 1
    else:
      self.host_index += len(buf)

    power_chunk = 1024
    power_start = 0
    powers = []
    min_power = 0.005
    while power_start + power_chunk < len(filtered_carrier):
      x = filtered_carrier[power_start:power_start+power_chunk]
      power = 0.9 * masking_power(x, self.sync_frequency, self.sample_rate)
      if power < min_power:
        power = min_power
      powers.append(power)
      power_start += power_chunk
    envelope = signal.resample(powers, len(buf))
    envelope = [ max(e, min_power) for e in envelope ]

    buf = np.multiply(buf, envelope)
    buf = np.multiply(buf, self.byte_window)
    buf = np.add(buf, filtered_carrier)

    return (shifts, list(buf))

  def __sine(self, (samples_start, samples_end), frequency, phase_shift = 0):
    return np.sin(2*np.pi*frequency/self.sample_rate * np.arange(samples_start, samples_end) + phase_shift)

  def __get_byte_window(self, slope_length = 120):
    slope = (np.sin(np.linspace(-np.pi/2, np.pi/2, slope_length)) + 1) / 2.0
    return np.concatenate((slope, np.ones(self.byte_buffer_size - 2 * slope_length), slope[::-1]))
