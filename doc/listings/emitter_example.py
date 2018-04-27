from emitter import Emitter
from Queue import Queue

queue = Queue()

# SYNTHESIS thread
fs = 44100 # sampling rate
host_sound = get_host_sound() # get host sound
payload = get_payload() # get payload data
sync_frequency = 8000.0 # setup frequencies
carrier_frequencies = [ 7000 + 100*i for i in range(0, 8) ]

em = Emitter(host_sound, fs, sync_frequency, carrier_frequencies, payload)
em.outstream(queue)

# PLAYING thread
while True:
  samples = queue.get(True) # blocking call to pop an item from queue
  if samples == False: # end of synthesized signal
    break
  else:
    play_samples(samples) # play sound with hardware
