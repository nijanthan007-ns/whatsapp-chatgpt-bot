from fastapi import FastAPI, Request
from pydantic import BaseModel
import httpx
import os
import openai
import asyncio

# Your credentials
ULTRAMSG_INSTANCE_ID = "instance133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"
OPENAI_API_KEY = "sk-proj-..."  # Replace with your full key

openai.api_key = OPENAI_API_KEY

app = FastAPI()

class WebhookMessage(BaseModel):
    event_type: str
    instanceId: str
    data: dict

@app.get("/")
async def root():
    return {"status": "running"}

@app.post("/webhook")
async def handle_webhook(msg: WebhookMessage):
    if msg.event_type == "message_received":
        user_message = msg.data.get("body")
        sender_number = msg.data.get("from")
        if not user_message or not sender_number:
            return {"status": "ignored"}

        print(f"📥 Incoming message from {sender_number}: {user_message}")

        # Step 1: Get response from OpenAI (New v1.0 syntax)
        try:
            response = await openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": user_message}
                ]
            )
            reply = response.choices[0].message.content.strip()
        except Exception as e:
            print("❌ OpenAI Error:", e)
            reply = "Sorry, something went wrong. Please try again later."

        # Step 2: Send reply back via UltraMsg
        payload = {
            "token": ULTRAMSG_TOKEN,
            "to": sender_number,
            "body": reply,
            "priority": "10",
            "referenceId": ""
        }

        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat",
                    data=payload
                )
        except Exception as e:
            print("❌ UltraMsg Error:", e)

    return {"status": "received"}
