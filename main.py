import os
import requests
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Get credentials from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# Initialize OpenAI
openai = OpenAI(api_key=OPENAI_API_KEY)

@app.get("/")
async def root():
    return {"message": "WhatsApp ChatGPT Bot is Live!"}

@app.post("/webhook")
async def receive_message(request: Request):
    payload = await request.json()
    print("📥 Incoming:", payload)

    try:
        if payload["event_type"] == "message_received":
            message_data = payload["data"]
            sender = message_data.get("from")
            message = message_data.get("body")

            if not sender or not message:
                return JSONResponse(content={"error": "Missing sender or message"}, status_code=400)

            print(f"💬 Message from {sender}: {message}")

            # Generate reply using OpenAI
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": message}]
            )

            reply = response.choices[0].message.content.strip()
            print("🤖 Reply:", reply)

            # Send reply using UltraMsg API
            send_url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
            send_payload = {
                "token": ULTRAMSG_TOKEN,
                "to": sender,
                "body": reply
            }

            send_response = requests.post(send_url, data=send_payload)
            print("📤 Sent message:", send_response.text)

        return {"success": True}

    except Exception as e:
        print("❌ Error:", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)
