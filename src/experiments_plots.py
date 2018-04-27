from __future__ import division
import os
from results import experiments
import matplotlib.pyplot as plt
from scipy.io import wavfile
import numpy as np
import scipy
from experiments.experiment import Experiment

CARRIER_DIR = "../sounds/carriers"
NOISE_DIR = "../sounds/noises"
OUTPUT_DIR = "../doc/figures/experiments"
CARRIER_FILENAMES = ["bach", "skalpel", "rockvocals"]
NOISE_FILENAMES = ["ambulance", "bottle-scratch", "keys", "crowd"]

# Psychoacoustics
results = {
        'bach.wav': 15,
        'rockvocals.wav': 8,
        'skalpel.wav': 11
}

plt.clf()
fig, ax = plt.subplots()
ax.set_ylim(0,20)
ax.set_xlim(0, 150)
ax.set_yticks([0,8,11,15,20])
ax.set_xticks([30, 75, 120])
ax.set_xticklabels(('bach.wav', 'rockvocals.wav', 'skalpel.wav'))
ax.bar([15, 60, 105], [15, 8, 11], 30, color='b')
ax.grid(True)
ax.set_xlabel("Sample")
ax.set_ylabel("Correct marks")
plt.savefig("{0}/psychoacoustic.png".format(OUTPUT_DIR), bbox_inches = 'tight', transparent=True)
print "Generated BAR plot for psychoacousitc test"


# Bit Error Rate
in_data = dict()
for experiment in experiments:
    carrier = experiment[0].split('/')[-1].split('.')[0]
    noise = experiment[2].split('/')[-1].split('.')[0]
    dB = experiment[3]
    correct = experiment[4]
    computed = experiment[5]
    if carrier not in in_data:
        in_data[carrier] = dict()
    if noise not in in_data[carrier]:
        in_data[carrier][noise] = dict()
    in_data[carrier][noise][int(dB)] = (correct, computed,)

for carrier in in_data.iterkeys():
    for noise in in_data[carrier].iterkeys():
        X = sorted(in_data[carrier][noise].keys())
        Y = []
        for x in X:
            data = in_data[carrier][noise][x]
            # print "ber for [{0},{1},{2}]: {3}".format(carrier, noise, x, BER(data[0], data[1]))
            Y.append(Experiment.BER(data[0], data[1]))
            # Y = [BER(in_data[carrier][noise][x][0], in_data[carrier][noise][x][1]) for x in X]
        plt.clf()
        plt.axis([-30, 0, 0, 1])
        plt.title('{0} with {1}'.format(carrier, noise))
        plt.xlabel('Noise amplitude (dB)')
        plt.ylabel('Bit error rate')
        plt.grid(True)
        plt.plot(X, Y, 'bo-')
        filename = "BER_{0}_{1}.png".format(carrier, noise)
        path = os.path.join(os.path.realpath('../doc/figures/experiments'), filename)
        plt.savefig(path, bbox_inches = 'tight', transparent=True)
        print "Generated BER plot for {0}/{1}".format(carrier, noise)


# Fast Fourier Transform
def plot_fft(input_filename, output_filename):
    sampFreq, data = wavfile.read(input_filename)

    data = np.array(data, dtype=np.float32)
    data = data[0:2**19]
    
    data /= np.amax(data)
    spectrum = np.fft.fft(data)
    size = len(spectrum)/2

    k = np.arange(len(data))
    T = len(data)/sampFreq
    freqs = k/T  

    plt.clf()
    plt.xlim(0,22000)
    # plt.ylim(-100,100)
    plt.ylim(0,40)
    plt.grid(True)
    plt.ylabel("Amplitude (dB)")
    plt.xlabel("Frequency (Hz)")
    xticks = np.arange(0, 22000, 4000)
    xticks = np.append(xticks, [8800])
    plt.xticks(xticks, rotation=60)
    plt.bar([7950], [40], 900, alpha=0.2, color='r')
    plt.plot(freqs, 10*np.log10(abs(spectrum)),'b-', alpha=0.5)
    plt.savefig(output_filename, bbox_inches = 'tight', transparent=True)
    print "Generated FFT plot for {0}".format(input_filename)
    
    
for noise in NOISE_FILENAMES:
    plot_fft("{0}/{1}.wav".format(NOISE_DIR, noise), "{0}/spectrum_{1}.png".format(OUTPUT_DIR, noise))
for carrier in CARRIER_FILENAMES:
    plot_fft("{0}/{1}.wav".format(CARRIER_DIR, carrier), "{0}/spectrum_{1}.png".format(OUTPUT_DIR, carrier))

plot_fft("../sounds/tests/bach_altered.wav", "../doc/figures/experiments/spectrum_bach_altered.png")
plot_fft("../sounds/tests/skalpel_altered.wav", "../doc/figures/experiments/skalpel_altered.png")
plot_fft("../sounds/tests/bach_payload.wav", "../doc/figures/experiments/spectrum_bach_payload.png")


