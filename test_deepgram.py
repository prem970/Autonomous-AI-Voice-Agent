import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

deepgram = DeepgramClient(api_key=os.getenv("DEEPGRAM_API_KEY"))

with open("call_audio.wav", "rb") as audio:
    buffer_data = audio.read()

response = deepgram.listen.v1.media.transcribe_file(
    request=buffer_data,
    model="nova-3",
    smart_format=True
)

print(
    response.results.channels[0].alternatives[0].transcript
)