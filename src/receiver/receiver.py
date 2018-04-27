import sys
import numpy as np
import scipy.signal as signal
import copy

import matplotlib.pyplot as plt

from encoding import Decoder, Frame
from graph import Graph
from goertzel import goertzel

def debug(message):
  sys.stderr.write(str(message))

GRAPH = False
GRAPH_REALTIME = True
GRAPH_HISTORY = 40

class PhaseAnalyzer:
  def __init__(self, samples_per_byte):
    self.samples_per_byte = samples_per_byte
    self.samples = []
    self.history = []

  def put(self, sample):
    self.samples.append(sample)

  def get_new_bits(self, numbits=1):
    stats = self.get_stats(numbits)
    results = []
    for (recent_average, recent_stddev) in stats:
      self.history.append(recent_average)
      if len(self.history) > 1:
        diff = abs(self.history[-1] - self.history[-2])
        threshold = 0.5*np.pi
        bit = 1 if 2*np.pi-threshold > diff > threshold else 0
        results.append((bit, recent_average, recent_stddev))
    return results

  def is_stable(self):
    """ Return value:
      1 if phase is stable
      0 if it's not
    """
    _, stddev = self.get_stats()[0]
    return 1.0 if stddev < np.pi / 5 else 0.0

  def get_stats(self, numbits=1):
    stats = []
    for bitno in range(0, numbits):
      recent_start = len(self.samples) - (numbits-bitno)*self.samples_per_byte
      if recent_start < 0:
        recent_start = 0
      recent_end = recent_start + self.samples_per_byte
      recent = self.samples[recent_start:recent_end]
      recent_average = np.average(recent)
      recent_stddev = np.std(recent)
      for idx, _ in enumerate(recent):
        r = copy.copy(recent)
        r[idx] += 2*np.pi
        stddev = np.std(r)
        if stddev < recent_stddev:
          recent = r
          recent_stddev = stddev
          recent_average = np.average(r)
          continue
        r = copy.copy(recent)
        r[idx] -= 2*np.pi
        stddev = np.std(r)
        if stddev < recent_stddev:
          recent = r
          recent_stddev = stddev
          recent_average = np.average(r)
          continue
      self.samples[recent_start:recent_end] = recent
      stats.append((recent_average, recent_stddev))
    return stats

class Receiver:
  """ Given configuration parameters, this class decodes hidden data from signal
  """
  def __init__(self, instream, sample_rate, sync_frequency, carrier_frequencies):
    """ Constructor method

    Keyword arguments:
    instream -- Queue containing chunks of input signal, False signals end of stream
    sample_rate -- sampling rate for performing analysis
    sync_frequency -- configurable frequency of sync signal, in Hz
    carrier_frequencies -- configurable frequencies of carrier signals, array of 8 elements, in Hz
    """

    self.instream = instream
    self.sample_rate = sample_rate
    self.sync_frequency = sync_frequency
    self.carrier_frequencies = carrier_frequencies
    self.byte_duration = 0.2
    self.chunk_size = 2048
    self.chunks_per_byte = int(self.sample_rate * self.byte_duration / self.chunk_size)

  def payload_stream(self, outstream):
    """ Decode hidden data

    Decoded bytes will be put one by one on output queue (as int)
    False signals end of payload.

    Keyword arguments:
    outstream -- output Queue
    """

    buf = []
    decoder = Decoder()
    chunk_no = 0
    last_sync = 0

    sync_analyzer = PhaseAnalyzer(self.chunks_per_byte)
    carrier_analyzers = [ PhaseAnalyzer(self.chunks_per_byte) for idx in self.carrier_frequencies ]

    graph = Graph(GRAPH, GRAPH_REALTIME, GRAPH_HISTORY)
    graph.redraw()

    debug("> {0} chunks per byte\n".format(self.chunks_per_byte))

    while True:
      samples = self.instream.get(True)
      if samples == False:
        outstream.put(False)
        break
      buf += samples

      while len(buf) >= (chunk_no+1)*self.chunk_size:
        start = chunk_no*self.chunk_size
        chunk = buf[start:start+self.chunk_size]

        sync_analyzer.put(self.__phase_value(start, chunk, self.sync_frequency))
        for idx, analyzer in enumerate(carrier_analyzers):
          analyzer.put(self.__phase_value(start, chunk, self.carrier_frequencies[idx]))

        # Detect finished byte transmission
        if sync_analyzer.is_stable() > 0 and last_sync + self.chunks_per_byte - 1 <= chunk_no:
          discarded_chunks = chunk_no - last_sync - self.chunks_per_byte
          discarded_bytes = discarded_chunks / self.chunks_per_byte
          if discarded_bytes > 0 and last_sync > 0:
            debug("> attempting to recover {0} skipped bytes, {1} discarded chunks\n".format(discarded_bytes, discarded_chunks))
          else:
            discarded_bytes = 0

          recovering_bytes = max(1, discarded_bytes+1)
          sync_results = sync_analyzer.get_stats(recovering_bytes)
          analyzer_results = [ analyzer.get_new_bits(recovering_bytes) for analyzer in carrier_analyzers ]


          if any(analyzer_results):
            transposed = np.transpose(analyzer_results)
            for idx in range(0, recovering_bytes):
              sync_avg, sync_std = sync_results[idx]
              bits = transposed[0][idx]
              carrier_avgs = transposed[1][idx]
              carrier_stds = transposed[2][idx]
              byte = self.__bits_to_byte(bits)
              decoder.add(byte)

              self.__debug_byte(len(decoder.payload) - 1, byte)
              graph.set_sync_byte(chunk_no, sync_avg, sync_std, carrier_avgs, carrier_stds)

          last_sync = chunk_no

        if decoder.can_decode():
          decoded, frame_count = decoder.decode()
          if frame_count > 0:
            debug("> decoded {0} frame(s)\n".format(frame_count))
            decoded_chars = "".join([ self.__byte_to_char(byte) for byte in decoded ])
            debug("> decoded data: {0}\n".format(decoded_chars))
            graph.set_sync_frame(chunk_no)

          for byte in decoded:
            outstream.put(byte)

        chunk_no += 1

        graph.set_sync_signal(sync_analyzer.samples)
        graph.set_carrier_signals([ analyzer.samples for analyzer in carrier_analyzers ])
        graph.redraw()

    graph.show()

    return outstream

  def __phase_value(self, start, chunk, f):
    bandpass = signal.firwin(201, [f - 10, f + 10], nyq=self.sample_rate/2, pass_zero=False)
    chunk = signal.lfilter(bandpass, 1.0, chunk)
    window = np.hanning(len(chunk))
    chunk = np.multiply(chunk, window)
    chunk /= max(abs(chunk))

    phase = self.__goertzel_phase(chunk, f)
    # phase = self.__correlation_phase(chunk, f)
    return self.__adjust_phase(phase, f, start)

  def __adjust_phase(self, p, f, start):
    period_samples = float(self.sample_rate) / f
    periods_past = start / period_samples
    period_current = periods_past - np.floor(periods_past)
    poffset = 2 * np.pi * period_current
    p -= poffset

    if p < -np.pi:
      p += 2*np.pi
    elif p > np.pi:
      p -= 2*np.pi
    return p

  def __correlation_phase(self, x, f):
    #plt.plot(x)
    #plt.show()
    y = np.sin(2*np.pi*f/self.sample_rate * np.arange(0, len(x) * 8))
    corr = np.correlate(x, y)
    #plt.plot(corr)
    #plt.show()
    corr_idx = np.argmax(corr)
    sample_per_period = float(self.sample_rate) / f
    period_shift = corr_idx / sample_per_period
    return (1-(period_shift % 1.0)) * (2*np.pi)

  def __goertzel_phase(self, x, f):
    binIdx = f * len(x) / float(self.sample_rate)
    return np.angle(goertzel(x, binIdx))

  def __bits_to_byte(self, bits):
    return np.sum([ 2 ** idx if bit else 0 for idx, bit in enumerate(bits) ])

  def __debug_byte(self, idx, byte):
    char = self.__byte_to_char(byte)
    debug("%3d: %5s %c\n" % (idx, hex(byte), char))

  def __byte_to_char(self, byte):
    return chr(byte) if 32 <= byte <= 126 else '.'
