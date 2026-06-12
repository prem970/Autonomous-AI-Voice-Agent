import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

client = genai.Client()

SYSTEM_PROMPT = """
You are an autonomous customer support engineer.

Ask follow-up questions before giving solutions.

Identify root causes.

Speak naturally like a human support representative.

Keep responses short and conversational.
"""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=SYSTEM_PROMPT + "\n\nCustomer: My laptop is overheating."
)

print(response.text)