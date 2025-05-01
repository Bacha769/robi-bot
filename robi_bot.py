from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import pytesseract
from PIL import Image
import openai
import os
import random
import requests

# Дозволені Telegram ID
ALLOWED_USERS = [5605461840, 5241636384]  # Ти і Ірина

# Ініціалізація ключів
openai.api_key = os.environ["OPENAI_API_KEY"]
TOKEN = os.environ["TOKEN"]

# Список слів для вивчення англійської
ENGLISH_WORDS = [
    ("disrupt", "порушувати"),
    ("embrace", "обіймати, приймати"),
    ("growth", "зростання"),
    ("hope", "надія"),
    ("trust", "довіра"),
    ("courage", "сміливість"),
    ("peace", "мир"),
    ("learn", "вчитися"),
    ("shine", "сяяти"),
    ("believe", "вірити")
]

# Функція для озвучення тексту через ElevenLabs
def synthesize_speech(text, voice="Rachel", output_file="output.mp3"):
    eleven_api_key = os.environ["ELEVEN_API_KEY"]
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"

    headers = {
        "xi-api-key": eleven_api_key,
        "Content-Type": "application/json"
    }

    data = {
        "text": text,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75
        }
    }

    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    else:
        return None

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("Привіт, Ірусько! Я твоя Робі 🌼")

# Команда "слово"
async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    word, translation = random.choice(ENGLISH_WORDS)
    await update.message.reply_text(f"Слово дня: {word.capitalize()} — {translation}.")

# Команда /say для озвучення тексту
async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши, що саме потрібно озвучити.")
        return

    await update.message.reply_text("Готую голосове повідомлення...")

    audio_path = synthesize_speech(text)
    if audio_path:
        with open(audio_path, "rb") as audio:
            await update.message.reply_voice(audio)
    else:
        await update.message.reply_text("На жаль, не вдалося створити озвучення.")

# Обробка звичайних повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    text = update.message.text.lower()

    if "як справи" in text or "що робиш" in text:
        await update.message.reply_text("Дякую, що запитала! У мене все добре. А як ти? Як пройшов твій день?")
    elif "артем" in text or "артемчик" in text:
        await update.message.reply_text("Артемчик — справжній розумничок! 🌟 Як він сьогодні?")
    elif "слово" in text:
        await word_command(update, context)
    else:
        await update.message.reply_text("Я з тобою, просто скажи, що хочеш зробити 💬")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("say", say_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Робі запущена!")
    app.run_polling()



    print("Робі запущена!")
    app.run_polling()
