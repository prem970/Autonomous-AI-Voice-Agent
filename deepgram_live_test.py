import os
from dotenv import load_dotenv
from deepgram import DeepgramClient

load_dotenv()

dg = DeepgramClient(
    api_key=os.getenv("DEEPGRAM_API_KEY")
)

print(dir(dg.listen))
print(dir(dg.listen.v1))