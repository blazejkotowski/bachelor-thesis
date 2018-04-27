from experiment import Experiment

host_path = 'host.wav'
noise_path = 'noise.wav'
payload_string = "Lorem ipsum dolor sit amet consectetur adipisicing elit"
payload = [ ord(l) for l in payload_string ]

experiment = Experiment(host_path, noise_path, 0.0, -10.0, payload)
decoded_payload = experiment.run()

ber = Experiment.ber(payload, decoded_payload)
