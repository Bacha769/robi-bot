from telegram import Update, InputFile
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
ELEVEN_API_KEY = os.environ["ELEVEN_API_KEY"]

# Список англійських слів
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

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    await update.message.reply_text("Привіт, Ірусько! Я твоя Робі 🌼")

# Команда /word
async def word_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return
    word, translation = random.choice(ENGLISH_WORDS)
    await update.message.reply_text(f"Слово дня: {word.capitalize()} — {translation}.")

# Команда /say
async def say_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("Будь ласка, додай текст після команди /say.")
        return

    try:
        response = requests.post(
            "https://api.elevenlabs.io/v1/text-to-speech/Yko7VS2Vq27utM5u2u0M/stream",
            headers={
                "xi-api-key": ELEVEN_API_KEY,
                "Content-Type": "application/json"
            },
            json={
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.4,
                    "similarity_boost": 0.7
                }
            }
        )
        with open("voice.mp3", "wb") as f:
            f.write(response.content)

        with open("voice.mp3", "rb") as audio:
            await update.message.reply_voice(voice=InputFile(audio))
    except Exception as e:
        await update.message.reply_text(f"Помилка озвучення: {e}")

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

# Обробка фото
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ALLOWED_USERS:
        return

    try:
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = "received_photo.jpg"
        await file.download_to_drive(file_path)

        text = pytesseract.image_to_string(Image.open(file_path), lang="eng+deu")
        await update.message.reply_text(f"Я знайшла на фото такий текст:\n{text.strip()}")
    except Exception as e:
        await update.message.reply_text(f"Не вдалося обробити фото: {e}")

# Запуск бота
if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("word", word_command))
    app.add_handler(CommandHandler("say", say_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    print("Робі запущена!")
    app.run_polling()
