from reedsolo import RSCodec, ReedSolomonError
import sys
import numpy as np

class Frame:
  """ Structure encoding single package of data, with preamble and error correction
  """

  preamble = [ 0x16, 0x16 ]
  preamble_size = len(preamble)
  payload_size = 16
  ecorr_size = 6
  size = preamble_size + payload_size + ecorr_size

  def __init__(self, payload):
    """ Constructor method

    Keyword arguments:
    payload -- array of int representing payload data (16 elements)
    """

    if len(payload) != Frame.payload_size:
      raise ValueError("payload must be {0} bytes in length".format(Frame.payload_size))
    self.payload = payload

  def bytes(self):
    """ Get full frame bytes

    Return type: array(int)
    """
    return Frame.preamble + self.__error_corrected()

  def __error_corrected(self):
    return list(RSCodec(Frame.ecorr_size).encode(self.payload))

class Encoder:
  """ Encodes bytes using error correction
  """

  def __init__(self, payload):
    """ Constructor method

    Keyword arguments:
    payload -- bytes to be encoded, array of int
    """
    self.payload = payload

  def encode(self):
    """ Encodes input bytes

    Return type: array(int)
    """

    fsize = Frame.payload_size
    padding = [ 0x00 ] * ((fsize - len(self.payload)) % fsize)
    buf = self.payload + padding
    out = []
    for i in range(0, len(buf) / fsize):
      chunk = buf[(i*fsize):(i+1)*fsize]
      out += Frame(chunk).bytes()
    return out

class Decoder:
  """ Decodes bytes of data applying error correction
  """

  def __init__(self):
    self.payload = []

  def add(self, byte):
    self.payload.append(byte)

  def can_decode(self):
    return len(self.payload) >= Frame.size

  def decode(self):
    """ Decodes input data

    Returns: (bytes, frame_count)
    bytes - array of int
    frame_count - int
    """

    if not self.can_decode():
      return ([], 0)

    outbytes = []
    corr_idx = [ self.__correlate_with_preamble(self.payload[idx:idx+Frame.preamble_size]) for idx, byte in enumerate(self.payload) ]

    corr_threshold = 7.0/8.0
    candidates = [ sum(filter(lambda x: x >= corr_threshold, corr_idx[idx::Frame.size])) for idx, corr in enumerate(corr_idx) ]
    fstart = np.argmax(candidates)
    frames_count = (len(self.payload) - fstart) / Frame.size
    if candidates[fstart] == 0:
      frames_count = 0
    fend = fstart+frames_count*Frame.size
    if frames_count > 0:
      for frame in np.array_split(self.payload[fstart:fend], frames_count):
        outbytes += self.__decode_frame_bytes(list(frame))
      self.payload = self.payload[fend:]
    return (outbytes, len(outbytes) / Frame.payload_size)

  def __correlate_with_preamble(self, bts):
    return 1.0 - sum([ bin(a ^ b).count('1') for (a, b) in zip(bts, Frame.preamble) ]) / (Frame.preamble_size * 8.0)

  def __decode_frame_bytes(self, bts):
    data = bts[Frame.preamble_size:(Frame.preamble_size + Frame.payload_size)]
    ecorr = bts[(Frame.preamble_size + Frame.payload_size):]
    try:
      decoded = RSCodec(Frame.ecorr_size).decode(data + ecorr)
      ecorr_bytes = sum([ byte != data[i] for i, byte in enumerate(decoded)])
      if ecorr_bytes > 0:
        sys.stderr.write("> corrected {0} bytes\n".format(ecorr_bytes))
      return decoded
    except ReedSolomonError:
      sys.stderr.write("> could not perform error correction!\n")
      return data
