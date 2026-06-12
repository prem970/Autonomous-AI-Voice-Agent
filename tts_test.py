audio_stream = dg.speak.v1.audio.generate(
    text="Hello, I am your AI support assistant.",
    model="aura-2-asteria-en",
    encoding="linear16",
    sample_rate=8000,
    container="none"
)

with open("response.raw", "wb") as f:
    for chunk in audio_stream:
        f.write(chunk)

print("response.raw created")