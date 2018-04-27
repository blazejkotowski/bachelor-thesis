from encoding import Decoder

stream1 = [22, 22, 104, 101, 108, 108, 111, 0, 0, 0, 0, 0]
stream2 = [0, 0, 0, 0, 0, 0, 210, 201, 10, 89, 213, 255]

decoder = Decoder()

for byte in stream1:
  decoder.add(byte)

decoder.can_decode() # False

for byte in stream2:
  decoder.add(byte)

decoder.can_decode() # True

# decoded single frame
# payload == [104, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
# frame_count == 1
payload, frame_count = decoder.decode()
