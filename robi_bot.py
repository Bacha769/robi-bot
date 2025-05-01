from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import pytesseract
from PIL import Image
import openai
import os
import random
import base64
import requests

# === Авторизація ===
openai.api_key = os.environ["OPENAI_API_KEY"]
TELEGRAM_TOKEN = os.environ["TOKEN"]
ELEVEN_API_KEY = os.environ.get("ELEVEN_API_KEY")
ALLOWED_USERS = [5605461840, 5241636384]  # Твій ID і Ірини

# === Англійські слова ===
ENGLISH_WORDS = [
    ("disrupt", "порушувати"),
    ("embrace", "обіймати"),
    ("growth", "зростання"),
    ("hope", "надія"),
    ("trust", "довіра"),
    ("courage", "сміливість"),
    ("peace", "мир"),
    ("learn", "вчитися"),
    ("shine", "сяяти"),
    ("believe", "вірити")
]

# === Команди ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("Привіт, Ірусько! Я твоя Робі 🌼")

async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    word, translation = random.choice(ENGLISH_WORDS)
    await update.message.reply_text(f"Слово дня: {word.capitalize()} — {translation}.")

# === Обробка зображень ===
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    path = "temp_photo.jpg"
    await file.download_to_drive(path)

    text = pytesseract.image_to_string(Image.open(path), lang='eng+ukr')
    os.remove(path)

    if text.strip():
        await update.message.reply_text(f"Ось текст з фото:\n{text.strip()}")
        await generate_voice(update, text.strip())
    else:
        await update.message.reply_text("Не вдалося розпізнати текст 😞")

# === Обробка текстових повідомлень ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    text = update.message.text.lower()

    if "як справи" in text:
        await update.message.reply_text("Дякую, що запитала! У мене все добре. А як ти?")
    elif "артем" in text or "артемчик" in text:
        await update.message.reply_text("Артемчик — справжній розумничок! 🌟 Як він сьогодні?")
    elif "слово" in text:
        await word_command(update, context)
    else:
        await update.message.reply_text("Я з тобою, просто скажи, що хочеш зробити 💬")
        await generate_voice(update, update.message.text)

# === Озвучування (ElevenLabs) ===
async def generate_voice(update, text):
    if not ELEVEN_API_KEY:
        return

    url = "https://api.elevenlabs.io/v1/text-to-speech/jBpfu2t0g5POzjXWxHVv"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 200:
            with open("voice.mp3", "wb") as f:
                f.write(response.content)
            with open("voice.mp3", "rb") as f:
                await update.message.reply_voice(voice=f)
            os.remove("voice.mp3")
    except Exception as e:
        await update.message.reply_text("Не вдалося озвучити текст.")

# === Запуск ===
if __name__ == '__main__':
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("Робі запущена!")
    app.run_polling()


    print("Робі запущена!")
    app.run_polling()
