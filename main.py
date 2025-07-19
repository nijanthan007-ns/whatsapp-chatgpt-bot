from fastapi import FastAPI, Request
from openai import OpenAI
import requests

app = FastAPI()

# Directly include your OpenAI API key here
client = OpenAI(api_key="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")

ULTRAMSG_URL = "https://api.ultramsg.com/instance133623/messages/chat"
ULTRAMSG_TOKEN = "shnmtd393b5963kq"

@app.get("/")
def root():
    return {"status": "working"}

@app.post("/webhook")
async def receive_message(request: Request):
    data = await request.json()
    message = data['data']['body']
    sender = data['data']['from']

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": message}]
        )
        reply = response.choices[0].message.content
    except Exception as e:
        print("❌ OpenAI Error:", str(e))
        reply = "⚠️ Sorry, I couldn't process that."

    payload = {
        "token": ULTRAMSG_TOKEN,
        "to": sender,
        "body": reply
    }

    requests.post(ULTRAMSG_URL, data=payload)
    return {"success": True}
