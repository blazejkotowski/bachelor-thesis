from Queue import Queue
from emitter.emitter import Emitter
from scipy.io import wavfile
import sys
import numpy as np

CARRIER_DIR = "../sounds/carriers"
TESTS_DIR = "../sounds/tests"
CARRIER_FILENAMES = ["skalpel", "bach", "rockvocals"]

short_message = "Lorem Ipsum is simply dummy text of the printing and typesetting industry"[:32]
payload = [ ord(l) for l in short_message ]

if __name__ == "__main__":
    for filename in CARRIER_FILENAMES:
        filepath = "{0}/{1}.wav".format(CARRIER_DIR, filename)

        carrier_fs, carrier_data = wavfile.read(filepath)
        carrier_data = np.array(carrier_data, dtype=np.float32)

        sync_frequency = 8800.0
        carrier_frequencies = [ 8003.3, 8105.2, 8209.7, 8318.0, 8399.4, 8521.1, 8587.1, 8691.6 ]
        out = Queue()
        emitter = Emitter(carrier_data, carrier_fs, sync_frequency, carrier_frequencies, payload)
        emitter.outstream(out)

        output_data = np.array([], dtype=np.float32)
        while True:
            bts = out.get(True)
            if bts == False:
                break
            output_data = np.append(output_data, bts)

        output_data = np.array(output_data, dtype=np.float32)

        payload_filepath = "{0}/{1}_payload.wav".format(TESTS_DIR, filename)
        wavfile.write(payload_filepath, carrier_fs, output_data)

        # altered_filepath = "{0}/{1}_altered.wav".format(TESTS_DIR, filename)
        # wavfile.write(altered_filepath, carrier_fs, output_data)

        # original_filepath = "{0}/{1}.wav".format(TESTS_DIR, filename)
        # wavfile.write(original_filepath, carrier_fs, carrier_data[:len(output_data)])

