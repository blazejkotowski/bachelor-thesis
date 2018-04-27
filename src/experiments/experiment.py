import pyaudio, numpy as np, wave, time, sys
from scipy.io import wavfile
from Queue import Queue
from struct import unpack

import emitter.emitter as em
import receiver.receiver as rc

class Experiment(object):
    """ Class to configure and run single experiment 
        
    Experiment definition:
    There are carrier sample and noise sample, and information to be dissimulated.
    Information is dissimulated in carrier sample by emitter, then it is played on one 
    channel, while noise sample is played on another channel. Both channels have
    specificied amplitude. Sum of noise carrier and noise is recorder on another channel.
    Recorded sample is passed to receiver in order to decrypt hidden information.
    """
    def __init__(self, carrier, noise, carrier_db=0, noise_db=0, payload=[]):
        """ Constructor method
        
        Keyword arguments:
        carrier -- wav file path carrying information
        noise -- wav file path with noise to be 
        carrier_db -- volume of carrier sample in dB
        noise_db -- volume of noise sample in dB
        """
        
        self.carrier = carrier
        self.noise = noise
        self.carrier_db = carrier_db
        self.noise_db = noise_db
        self.carrier_mag = 10.0**(carrier_db/20.0)
        self.noise_mag = 10.0**(noise_db/20.0)
        self.blocksize = 1024
        self.playing = False
        self.payload = payload

    def run(self):
        """ Run experiment
        
        Return type: tuple(BER, SNR)
        BER -- Bit error rate
        SNR -- Signal to noise before recording
        """

        # Read samples
        carrier_fs, carrier_data = wavfile.read(self.carrier)
        noise_fs, noise_data = wavfile.read(self.noise)

        if noise_fs != carrier_fs:
            print "Sorry, noise and carrier sampling rate should be the same"
            sys.exit(-1)

        # Hardware configuration
        channel_map = (0, 1)
        try:
            stream_info = pyaudio.PaMacCoreStreamInfo(
                flags=pyaudio.PaMacCoreStreamInfo.paMacCorePlayNice, # default
                channel_map=channel_map)
        except AttributeError:
            print("Sorry, couldn't find PaMacCoreStreamInfo. Make sure that "
                    "you're running on Mac OS X.")
            sys.exit(-1)

        # Convert to float32 format
        carrier_data = np.array(carrier_data, dtype=np.float32)
        noise_data = np.array(noise_data, dtype=np.float32)

        # start emitter
        sample_rate = carrier_fs
        sync_frequency = 8800.0
        carrier_frequencies = [ 8003.3, 8105.2, 8209.7, 8318.0, 8399.4, 8521.1, 8587.1, 8691.6 ]
        out = Queue()
        emitter = em.Emitter(carrier_data, sample_rate, sync_frequency, carrier_frequencies, self.payload)
        emitter.outstream(out)
        carrier_data = np.array([], dtype=np.float32)
        while True:
          bts = out.get(True)
          if bts == False:
            break
          carrier_data = np.append(carrier_data, bts)
        carrier_data = np.array(carrier_data, dtype=np.float32)

        print "signal synthesized {0}".format(len(carrier_data))
        # end emitter

        # Normalization
        carrier_data /= max(carrier_data)
        noise_data /= max(noise_data)

        # Mix carrier with noise
        out_data = self._mix(carrier_data, noise_data, self.carrier_mag, self.noise_mag)
        
        # Insert second of silence in beginning
        out_data = np.append(np.zeros(carrier_fs*2, dtype=np.float32), out_data)

        # Init pyaudio object
        pa = pyaudio.PyAudio()

        # Stream to play audio
        out_stream = pa.open(format = pyaudio.paFloat32,
                channels = 2,
                rate = carrier_fs,
                output = True,
                stream_callback = self._output_callback(out_data),
                output_host_api_specific_stream_info = stream_info,
                frames_per_buffer=10000,
                output_device_index = 2)

        print "im sleeping"
        time.sleep(1)
        print "waking up"

        print "playing..."
        
        def in_callback(in_data, frames_count, time_info, status):
            in_callback.recorded_string += in_data
            return (None, pyaudio.paContinue)
        in_callback.recorded_string = ""

        # Stream to record audio
        in_stream = pa.open(format = pyaudio.paFloat32,
                channels = 1,
                rate = carrier_fs,
                input_device_index = 2,
                frames_per_buffer=10000,
                stream_callback = in_callback,
                input = True)

        # Recording
        out_stream.start_stream() # Start playing
        in_stream.start_stream()

        record_padding = 8
        while(out_stream.is_active() or record_padding > 0):
            time.sleep(0.1)
            if not out_stream.is_active():
                record_padding -= 1

        time.sleep(1)

        print "recorded"

        # Stop recording stream
        in_stream.stop_stream()
        in_stream.close()
        
        recorded_data = np.fromstring(in_callback.recorded_string, dtype=np.float32)

        # Stop playing stream
        out_stream.stop_stream()
        out_stream.close()

        # Preview recorded audio
        # out_stream = pa.open(format = pyaudio.paFloat32,
        #         channels = 1,
        #         rate = carrier_fs,
        #         output = True,
        #         stream_callback = self._output_callback(recorded_data, channels = 1),
        #         output_host_api_specific_stream_info = stream_info,
        #         frames_per_buffer=self.blocksize,
        #         output_device_index = 2)

        # while(out_stream.is_active()):
        #     time.sleep(0.1)

        # out_stream.stop_stream()
        # out_stream.close()

        print "recorded {0} samples".format(len(recorded_data))
        rec = Queue()
        out = Queue()
        rec.put(recorded_data.tolist())
        rec.put(False)
        receiver = rc.Receiver(rec, carrier_fs, sync_frequency, carrier_frequencies)
        receiver.payload_stream(out)

        decoded = []
        while True:
          byte = out.get(True)
          if byte == False:
            break
          decoded.append(byte)
        char_payload = [ chr(byte) if 32 <= byte <=126 else '.' for byte in decoded ]
        print "decoded payload: " + "".join(char_payload)

        with open('experiment_ouptut.txt', 'a') as output:
            output.write("experiments.append('{0}', '{1}', '{2}', '{3}', [{4}], [{5}])\n".format(
                self.carrier,
                self.carrier_db,
                self.noise,
                self.noise_db,
                self.payload,
                ",".join(np.array(decoded, dtype=np.str))
            ))

        pa.terminate()

        return decoded

    @staticmethod
    def BER(correct, computed):
        total_errors = len(correct) - len(computed) # All not transmitted bits are errors
        for i in range(len(computed)):
            if correct[i] != computed[i]:
                total_errors += 1
        return total_errors/float(len(correct))

    @staticmethod
    def _mix(carrier, noise, carrier_mag, noise_mag):
        """ Function mixes carrier with noise, applying given magnitude """

        carrier *= carrier_mag
        noise *= noise_mag
        
        while len(noise) < len(carrier):
            noise = noise.append(noise)
        noise = noise[:len(carrier)]

        mixed = np.array([carrier, noise]).transpose().flatten()
        return mixed

        
    def _output_callback(self, wav_data, channels=2):
        """ Callback function generator for pyaudio output stream 
        
        Keyword arguments:
        wav_data -- data array, output should be read from
        """

        def callback(in_data, frame_count, time_info, status):
            frame_count *= channels
            pos = callback.pos
            out_data = wav_data[pos:pos+frame_count]
            callback.pos += frame_count
            return (out_data, pyaudio.paContinue)
        callback.pos = 0

        return callback
