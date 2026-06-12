from scipy.io.wavfile import write
import numpy as np

with open("call_audio.raw", "rb") as f:
    raw_data = f.read()

audio = np.frombuffer(raw_data, dtype=np.int16)

write("call_audio.wav", 8000, audio)

print("WAV file created!")