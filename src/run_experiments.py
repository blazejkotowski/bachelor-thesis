import numpy as np
import sys
from experiments.experiment import Experiment

CARRIER_DIR = "../sounds/carriers/"
NOISE_DIR = "../sounds/noises/"

CARRIER_FILENAMES = ["skalpel.wav", "bach.wav", "rockvocals.wav"]
NOISE_FILENAMES = ["keys.wav", "crowd.wav", "bottle-scratch.wav", "ambulance.wav"]

NOISE_DB_STEP = 5 
NOISE_DB_MIN = -30
NOISE_DB_MAX = 1

short_message = "Lorem Ipsum is simply dummy text of the printing and typesetting industry"[:32]
long_message = "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book."
payload = [ ord(l) for l in short_message ]

current_carrier = sys.argv[1]
current_noise = sys.argv[2]
current_db = sys.argv[3]

for carrier_filename in CARRIER_FILENAMES:
    if(CARRIER_FILENAMES.index(current_carrier) <= CARRIER_FILENAMES.index(carrier_filename)):
        for noise_filename in NOISE_FILENAMES:
            if(CARRIER_FILENAMES.index(current_carrier) < CARRIER_FILENAMES.index(carrier_filename) or
                    NOISE_FILENAMES.index(current_noise) <= NOISE_FILENAMES.index(noise_filename)):
                noise_path = NOISE_DIR + noise_filename
                carrier_path = CARRIER_DIR + carrier_filename
                for noise_db in np.arange(NOISE_DB_MIN, NOISE_DB_MAX, NOISE_DB_STEP):
                    if(CARRIER_FILENAMES.index(current_carrier) < CARRIER_FILENAMES.index(carrier_filename) or
                            NOISE_FILENAMES.index(current_noise) < NOISE_FILENAMES.index(noise_filename) or
                            noise_db >= float(current_db)):
                        experiment = Experiment(carrier_path, noise_path, 0.0, noise_db, payload)
                        print "Running experiment for carrier '{0}' mixed with noise '{1}' ({2}dB).".format(carrier_filename, noise_filename, noise_db) 
                        experiment.run()
