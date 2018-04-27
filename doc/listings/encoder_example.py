from encoding import Encoder

payload = [104, 101, 108, 108, 111] # "hello" in ASCII, 5 bytes

# encoded single frame
# [22, 22, 104, 101, 108, 108, 111, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 210, 201, 10, 89, 213, 255]
stream = Encoder(payload).encode()
