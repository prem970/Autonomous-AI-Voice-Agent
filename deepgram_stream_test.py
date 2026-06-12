from deepgram import DeepgramClient
from dotenv import load_dotenv
import os

load_dotenv()

dg = DeepgramClient(
    api_key=os.getenv("DEEPGRAM_API_KEY")
)

cm = dg.listen.v1.connect(
    model="nova-3",
    language="en",
    sample_rate=8000,
    encoding="linear16",
    interim_results=True,
    smart_format=True
)

conn = cm.__enter__()

print("CONNECTED")

print("recv =", conn.recv)
print("send_media =", conn.send_media)
print("start_listening =", conn.start_listening)

cm.__exit__(None, None, None)