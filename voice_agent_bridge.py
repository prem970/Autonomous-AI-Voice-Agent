import asyncio
import websockets
import json
import base64
import os

from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("EXOTEL CONNECTED")

    dg = await websockets.connect(
        "wss://agent.deepgram.com/v1/agent/converse",
        additional_headers={
            "Authorization": f"Token {DEEPGRAM_API_KEY}"
        }
    )

    print("DEEPGRAM CONNECTED")

    welcome = await dg.recv()

    print("WELCOME:")
    print(welcome)

    settings = {
        "type": "Settings",
        "audio": {
            "input": {
                "encoding": "linear16",
                "sample_rate": 8000
            },
            "output": {
                "encoding": "linear16",
                "sample_rate": 8000,
                "container": "none"
            }
        }
    }

    await dg.send(json.dumps(settings))

    print("SETTINGS SENT")

    stream_sid = None

    async def exotel_to_deepgram():

        nonlocal stream_sid

        while True:

            try:

                msg = await websocket.receive_text()

                data = json.loads(msg)

                event = data.get("event")

                if event == "start":

                    stream_sid = data.get("stream_sid")

                    print("STREAM SID:", stream_sid)

                elif event == "media":

                    audio = base64.b64decode(
                        data["media"]["payload"]
                    )

                    await dg.send(audio)

                elif event == "stop":

                    print("CALL ENDED")

                    await dg.close()

                    break

            except Exception as e:

                print("EXOTEL ERROR:", e)

                break

    async def deepgram_to_exotel():

        while True:

            try:

                response = await dg.recv()

                if isinstance(response, bytes):

                    print(
                        f"AGENT AUDIO RECEIVED: {len(response)} bytes"
                    )

                    if stream_sid:

                        payload = base64.b64encode(
                            response
                        ).decode()

                        await websocket.send_text(
                            json.dumps({
                                "event": "media",
                                "stream_sid": stream_sid,
                                "media": {
                                    "payload": payload
                                }
                            })
                        )

                else:

                    print("DEEPGRAM:")
                    print(response)

            except Exception as e:

                print("DG CLOSED:", e)

                break

    await asyncio.gather(
        exotel_to_deepgram(),
        deepgram_to_exotel()
    )