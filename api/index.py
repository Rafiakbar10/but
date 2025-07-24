from flask import Flask, request
import telegram
import os

TOKEN = os.environ.get("7898219623:AAHRUFZkJ_CjPGAYLjbYoJWchFrg9q7dvQM")
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route("/api", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        bot.send_message(chat_id, f"✅ Pesan diterima: {text}")
    return "ok"
