from fastapi import FastAPI, Request
from pydantic import BaseModel
import requests
from openai import OpenAI

# ==== YOUR CONFIGURATION ====
ULTRAMSG_INSTANCE_ID = "instance133623"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"
ULTRAMSG_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

# ==== HARDCODED OPENAI KEY ====
client = OpenAI(api_key="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")

# ==== FASTAPI SETUP ====
app = FastAPI()

# ==== WHATSAPP SENDER ====
def send_whatsapp_message(to, message):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message,
    }
    response = requests.post(ULTRAMSG_URL, json=payload)
    print("📤 WhatsApp sent:", response.text)
    return response.json()

# ==== HEALTH CHECK ====
@app.get("/")
def read_root():
    return {"status": "running"}

# ==== WEBHOOK HANDLER ====
@app.post("/webhook")
async def webhook(request: Request):
    try:
        data = await request.json()
        print("📥 Incoming message:", data)

        message_body = data["data"]["body"]
        sender = data["data"]["from"]

        # Ask OpenAI
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Reply like a friendly assistant."},
                {"role": "user", "content": message_body}
            ]
        )

        reply = response.choices[0].message.content.strip()
        print(f"🤖 Reply: {reply}")

        send_whatsapp_message(sender, reply)

    except Exception as e:
        import traceback
        print("❌ Exception occurred:")
        traceback.print_exc()
        try:
            send_whatsapp_message(sender, "⚠ Sorry, I couldn't process that.")
        except:
            pass

    return {"success": True}
