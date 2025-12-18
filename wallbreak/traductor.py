
import sounddevice as sd

devices = sd.query_devices()

for device in devices:
    print(device)