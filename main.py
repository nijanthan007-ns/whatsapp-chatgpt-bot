import os
import requests
from fastapi import FastAPI, Request
from pydantic import BaseModel
from openai import OpenAI
from fastapi.responses import JSONResponse

app = FastAPI()

# Your API keys
OPENAI_API_KEY = "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"  # Replace with your actual key
ULTRAMSG_INSTANCE_ID = "instance133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

# Ultramsg API endpoint
def send_whatsapp_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message
    }
    response = requests.post(url, data=payload)
    print("📤 Sent:", response.text)
    return response.status_code == 200

@app.get("/")
def home():
    return {"status": "Bot is running 🚀"}

@app.post("/webhook")
async def webhook(request: Request):
    try:
        payload = await request.json()
        print("📥 Incoming message:", payload)

        # Extract sender and message
        message_data = payload.get("data", {})
        sender = message_data.get("from", "")
        message_body = message_data.get("body", "")

        if not sender or not message_body:
            return JSONResponse(content={"status": "ignored"}, status_code=200)

        # Generate OpenAI response
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": message_body}
            ]
        )
        reply = response.choices[0].message.content.strip()

        # Send reply back to user
        send_whatsapp_message(sender, reply)

    except Exception as e:
        print("❌ Error:", str(e))

    return JSONResponse(content={"status": "ok"}, status_code=200)
