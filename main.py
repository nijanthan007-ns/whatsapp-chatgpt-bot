from fastapi import FastAPI, Request
import httpx
import os
import openai

app = FastAPI()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")
ULTRAMSG_API_URL = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"

openai.api_key = OPENAI_API_KEY

@app.get("/")
def root():
    return {"message": "✅ WhatsApp ChatGPT Bot is running."}

@app.post("/webhook")
async def whatsapp_webhook(req: Request):
    body = await req.json()
    print("\U0001F4E5 Incoming:", body)

    try:
        if body.get("event_type") == "message_received":
            msg_data = body.get("data", {})
            sender = msg_data.get("from")
            message = msg_data.get("body")

            if sender and message:
                response = await ask_openai(message)
                await send_reply(sender, response)

    except Exception as e:
        print("Error:", str(e))

    return {"status": "ok"}

async def ask_openai(prompt):
    try:
        res = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        return res.choices[0].message.content.strip()
    except Exception as e:
        return f"Error from OpenAI: {str(e)}"

async def send_reply(to_number, message):
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to_number,
        "body": message
    }
    async with httpx.AsyncClient() as client:
        res = await client.post(ULTRAMSG_API_URL, data=payload)
        print("\U0001F4E4 Sent:", res.json())
