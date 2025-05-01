from telegram import Update, InputFile
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import pytesseract
from PIL import Image
import openai
import os
import random
import requests
from deep_translator import GoogleTranslator

# Дозволені Telegram ID
ALLOWED_USERS = [5605461840, 5241636384]

# API ключі
openai.api_key = os.environ["OPENAI_API_KEY"]
TOKEN = os.environ["TOKEN"]
ELEVEN_API_KEY = os.environ["ELEVEN_API_KEY"]

# Список англійських слів
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

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("Привіт, Ірусько! Я твоя Робі 🌼")

# Озвучення тексту (англійська або німецька)
def synthesize_speech(text, lang="de", voice="Rachel", output_file="output.mp3"):
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice}"
    headers = {
        "xi-api-key": ELEVEN_API_KEY,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
    }
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 200:
        with open(output_file, "wb") as f:
            f.write(response.content)
        return output_file
    return None

# /say текст
async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Напиши, що саме потрібно озвучити.")
        return
    await update.message.reply_text("🎤 Готую голосове повідомлення...")
    path = synthesize_speech(text)
    if path:
        with open(path, "rb") as f:
            await update.message.reply_voice(f)
    else:
        await update.message.reply_text("❌ Не вдалося озвучити текст.")

# /слово
async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    word, translation = random.choice(ENGLISH_WORDS)
    await update.message.reply_text(f"Слово дня: {word} — {translation}.")

# Фото з текстом: витяг, переклад, озвучення
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    photo = update.message.photo[-1]
    file = await context.bot.get_file(photo.file_id)
    image_path = "image.jpg"
    await file.download_to_drive(image_path)

    text = pytesseract.image_to_string(Image.open(image_path), lang="deu")
    if not text.strip():
        await update.message.reply_text("Текст не знайдено.")
        return

    await update.message.reply_text(f"📝 Я знайшла текст:\n{text.strip()}")

    translated = GoogleTranslator(source="de", target="uk").translate(text)
    await update.message.reply_text(f"📘 Переклад:\n{translated.strip()}")

    audio_path = synthesize_speech(text.strip())
    if audio_path:
        with open(audio_path, "rb") as f:
            await update.message.reply_voice(f)

# Обробка повідомлень
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    text = update.message.text.lower()

    if "артем" in text:
        await update.message.reply_text("Артемчик — справжній розумничок! 🧠")
    elif "слово" in text:
        await word_command(update, context)
    elif "як справи" in text or "що робиш" in text:
        await update.message.reply_text("Я тут і думаю про тебе 🌸")
    else:
        await update.message.reply_text("Я з тобою, просто скажи, що хочеш 💬")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("say", say_command))
    app.add_handler(CommandHandler("слово", word_command))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Робі запущена!")
    app.run_polling()

