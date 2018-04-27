#!/usr/bin/env python

import numpy as np
from threading import Thread
from Queue import Queue
import random

import emitter.emitter as em
import receiver.receiver as rc

short_message = "Lorem Ipsum is simply dummy text of the printing and typesetting industry"
long_message = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
payload = [ ord(l) for l in short_message ]
sample_rate = 44100
carrier = np.array([ 2*random.random() - 1 for i in range(0, 3*sample_rate) ]) # white noise

def tone(i):
  wiggle = (random.random() - 0.5) * 10
  return 100 * i + wiggle

sync_frequency = tone(88)
carrier_frequencies = [ tone(80+i) for i in range(0, 8) ]

out = Queue()
payload_stream = Queue()

def emit():
  emt = em.Emitter(carrier, sample_rate, sync_frequency, carrier_frequencies, payload)
  emt.outstream(out)

Thread(target=emit).start()

print "Decoding payload..."

rcv = rc.Receiver(out, sample_rate, sync_frequency, carrier_frequencies)
rcv.payload_stream(payload_stream)

print "Decoded payload:"

decoded = []
while True:
  byte = payload_stream.get(True)
  if byte == False:
    break
  decoded.append(byte)

char_payload = [ chr(byte) if 32 <= byte <=126 else '.' for byte in decoded ]
print "".join(char_payload)

exit(0)

import pyaudio

pa = pyaudio.PyAudio()
stream = pa.open(format=pyaudio.paFloat32,
  channels=1,
  rate=44100,
  output=True,
  frames_per_buffer=1024)

outpack = np.array(out, dtype=np.float32).tostring()
stream.write(outpack)
