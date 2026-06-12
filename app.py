from fastapi import FastAPI, WebSocket
from starlette.websockets import WebSocketDisconnect
import json
import base64
import wave
import numpy as np
import os
from dotenv import load_dotenv
from deepgram import DeepgramClient
from google import genai

load_dotenv()

app = FastAPI()

deepgram = DeepgramClient(
    api_key=os.getenv("DEEPGRAM_API_KEY")
)

gemini = genai.Client()

audio_buffer = bytearray()
current_stream_sid = None

SYSTEM_PROMPT = """
You are an autonomous customer support engineer.

Ask follow-up questions before giving solutions.

Identify root causes.

Speak naturally like a human support representative.

Keep responses short and conversational.
"""

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    global audio_buffer
    global current_stream_sid

    await websocket.accept()

    print("VOICEBOT CONNECTED")

    try:
        while True:

            message = await websocket.receive()

            if "text" not in message:
                continue

            data = json.loads(message["text"])

            event = data.get("event")

            # START EVENT
            if event == "start":

                current_stream_sid = data.get("stream_sid")

                print("\nSTREAM SID:")
                print(current_stream_sid)

                continue

            # MEDIA EVENT
            if event == "media":

                payload = data["media"]["payload"]

                audio_chunk = base64.b64decode(payload)

                audio_buffer.extend(audio_chunk)

                continue

            # STOP EVENT
            if event == "stop":

                print("\nCALL ENDED")

                # SAVE RAW AUDIO
                with open("call_audio.raw", "wb") as f:
                    f.write(audio_buffer)

                # RAW -> WAV
                audio = np.frombuffer(
                    audio_buffer,
                    dtype=np.int16
                )

                with wave.open("call_audio.wav", "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(2)
                    wf.setframerate(8000)
                    wf.writeframes(audio.tobytes())

                print("WAV CREATED")

                # DEEPGRAM STT
                with open("call_audio.wav", "rb") as audio_file:
                    buffer_data = audio_file.read()

                response = deepgram.listen.v1.media.transcribe_file(
                    request=buffer_data,
                    model="nova-3",
                    smart_format=True
                )

                transcript = (
                    response.results.channels[0]
                    .alternatives[0]
                    .transcript
                )

                print("\nCUSTOMER:")
                print(transcript)

                # GEMINI
                try:

                    ai_response = gemini.models.generate_content(
                        model="gemini-2.5-flash",
                        contents=f"""
{SYSTEM_PROMPT}

Customer:
{transcript}
"""
                    )

                    response_text = ai_response.text

                except Exception as e:

                    print("Gemini Error:", e)

                    response_text = (
                        "I am sorry. I am currently unavailable."
                    )

                print("\nAI RESPONSE:")
                print(response_text)

                # DEEPGRAM TTS
                print("\nGENERATING AI VOICE...")

                audio_stream = deepgram.speak.v1.audio.generate(
                    text=response_text,
                    model="aura-2-asteria-en",
                    encoding="linear16",
                    sample_rate=8000,
                    container="none"
                )

                with open("response.raw", "wb") as f:
                    for chunk in audio_stream:
                        f.write(chunk)

                print("AI AUDIO CREATED -> response.raw")

                # RESET
                audio_buffer = bytearray()

    except WebSocketDisconnect:
        print("Call completed")

    except Exception as e:
        print("ERROR:")
        print(e)