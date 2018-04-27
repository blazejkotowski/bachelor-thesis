from receiver import Receiver
from Queue import Queue

recorded_queue = Queue()
payload_queue = Queue()

# ANALYSIS thread
fs = 44100
sync_frequency = 8000.0 # setup frequencies
carrier_frequencies = [ 7000 + 100*i for i in range(0, 8) ]

rc = Receiver(recorded_queue, fs, sync_frequency, carrier_frequencies)
rc.payload_stream(payload_queue)

# RECORDING thread
while True:
  samples = device.record()
  recorded_queue.put(samples)

# OUTPUT thread
data = []
while True:
  byte = payload_queue.get(True) # blocking call to pop a byte from the queue
  if byte == False: # end of data
    print "decoded data: {0}".format(payload)
    break
  else:
    data.append(byte)

