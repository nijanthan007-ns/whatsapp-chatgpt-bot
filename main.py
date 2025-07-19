import os
import requests
from fastapi import FastAPI, Request
import openai
from dotenv import load_dotenv

load_dotenv()  # Load environment variables

openai.api_key = os.getenv("OPENAI_API_KEY")
ULTRAMSG_INSTANCE_ID = os.getenv("ULTRAMSG_INSTANCE_ID")
ULTRAMSG_TOKEN = os.getenv("ULTRAMSG_TOKEN")

app = FastAPI()

def send_whatsapp_message(to: str, text: str):
    url = f"https://api.ultramsg.com/{ULTRAMSG_INSTANCE_ID}/messages/chat"
    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": to,
        "body": text
    }
    requests.post(url, data=payload)

def get_ai_reply(prompt: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenAI error:", e)
        return "I'm having trouble right now. Please try again later."

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    if "body" in data and "from" in data:
        user_message = data["body"]
        user_number = data["from"].replace("whatsapp:", "")
        ai_reply = get_ai_reply(user_message)
        send_whatsapp_message(user_number, ai_reply)
    return {"success": True}

@app.get("/")
def root():
    return {"message": "WhatsApp AI Chatbot is running"}
