from fastapi import FastAPI, WebSocket

app = FastAPI()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):

    await websocket.accept()

    print("VOICEBOT CONNECTED")

    try:

        while True:

            message = await websocket.receive()

            print("\n" + "=" * 80)
            print("RAW MESSAGE")
            print("=" * 80)
            print(message)

            if message["type"] == "websocket.disconnect":
                print("\nCALL DISCONNECTED")
                break

    except Exception as e:
        print("\nERROR:")
        print(e)