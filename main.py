import os
import openai
import requests
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# ✅ Load environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

# ✅ Init OpenAI client
openai.api_key = OPENAI_API_KEY

# ✅ Init FastAPI app
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Function to get ChatGPT reply
def get_openai_response(message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4" if your key supports it
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": message},
            ],
            max_tokens=1000,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "Sorry, something went wrong while generating a reply."

# ✅ Function to send WhatsApp message via UltraMsg
def send_message(to, message):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": message,
    }
    try:
        response = requests.post(url, data=payload)
        print("UltraMsg send response:", response.text)
    except Exception as e:
        print("UltraMsg send error:", e)

# ✅ Webhook endpoint
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()
    print("📥 Incoming:", data)

    # Check if message has text
    if 'body' not in data or 'from' not in data:
        return {"success": False}

    sender = data['from']
    message = data['body']

    # Get response from ChatGPT
    reply = get_openai_response(message)

    # Send reply back to sender
    send_message(sender, reply)

    return {"success": True}
