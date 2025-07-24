import os
import requests
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from pytube import YouTube

# Token langsung ditulis (tidak pakai os.getenv)
TOKEN = "7898219623:AAHRUFZkJ_CjPGAYLjbYoJWchFrg9q7dvQM"
REQUEST_TIMEOUT = 30

# Inisialisasi Flask & Telegram bot
app = Flask(__name__)
telegram_app = Application.builder().token(TOKEN).build()

@app.route("/", methods=["GET"])
def home():
    return "🤖 Bot aktif!"

@app.route("/", methods=["POST"])
async def webhook():
    update = Update.de_json(request.get_json(force=True), telegram_app.bot)
    await telegram_app.process_update(update)
    return "OK"

# Perintah /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🎬 Kirim link Instagram / TikTok / YouTube untuk mengunduh video.")

# Fungsi download dari YouTube
def download_youtube(url):
    try:
        yt = YouTube(url)
        stream = yt.streams.get_highest_resolution()
        stream.download(filename="video.mp4", timeout=REQUEST_TIMEOUT)
        return open("video.mp4", "rb")
    except Exception as e:
        print(f"Error YouTube: {e}")
        return None

# Fungsi download dari TikTok
def download_tiktok(url):
    try:
        api_url = f"https://tikwm.com/api/?url={url}"
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT).json()
        video_url = response["data"]["play"]
        video_data = requests.get(video_url, timeout=REQUEST_TIMEOUT).content
        with open("tiktok.mp4", "wb") as f:
            f.write(video_data)
        return open("tiktok.mp4", "rb")
    except Exception as e:
        print(f"Error TikTok: {e}")
        return None

# Fungsi download dari Instagram
def download_instagram(url):
    try:
        api_url = f"https://api.instagram.com/oembed/?url={url}"
        response = requests.get(api_url, timeout=REQUEST_TIMEOUT).json()
        media_url = response["thumbnail_url"]
        media_data = requests.get(media_url, timeout=REQUEST_TIMEOUT).content
        with open("instagram.mp4", "wb") as f:
            f.write(media_data)
        return open("instagram.mp4", "rb")
    except Exception as e:
        print(f"Error Instagram: {e}")
        return None

# Handler pesan teks (link)
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "instagram.com" in text:
        await update.message.reply_text("⏳ Unduh dari Instagram...")
        video = await asyncio.to_thread(download_instagram, text)
    elif "tiktok.com" in text:
        await update.message.reply_text("⏳ Unduh dari TikTok...")
        video = await asyncio.to_thread(download_tiktok, text)
    elif "youtube.com" in text or "youtu.be" in text:
        await update.message.reply_text("⏳ Unduh dari YouTube...")
        video = await asyncio.to_thread(download_youtube, text)
    else:
        await update.message.reply_text("❌ Link tidak dikenali.")
        return

    if video:
        await update.message.reply_video(video=video, caption="✅ Sukses diunduh!", write_timeout=REQUEST_TIMEOUT)
        video.close()
        os.remove(video.name)
    else:
        await update.message.reply_text("❌ Gagal mengunduh. Coba lagi.")

# Tambahkan handler
telegram_app.add_handler(CommandHandler("start", start))
telegram_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))