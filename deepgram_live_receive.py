from deepgram import DeepgramClient
from deepgram.core.events import EventType
from dotenv import load_dotenv
import os

load_dotenv()

def on_message(message):
    print("MESSAGE:")
    print(message)

dg = DeepgramClient(
    api_key=os.getenv("DEEPGRAM_API_KEY")
)

with dg.listen.v1.connect(
    model="nova-3",
    language="en",
    encoding="linear16",
    sample_rate=8000,
    interim_results=True,
    smart_format=True
) as conn:

    conn.on(EventType.MESSAGE, on_message)

    print("CONNECTED")

    conn.start_listening()

    input("Press Enter to exit...")