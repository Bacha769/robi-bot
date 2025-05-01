from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import pytesseract
from PIL import Image
import openai
import os
import random

import os
openai.api_key = os.environ["OPENAI_API_KEY"]
TOKEN = os.environ["TOKEN"]

FRIENDLY_REPLIES = [
    "Привіт, Рибко! Як ти сьогодні? 💖",
    "Ти молодчинка, Ірусько! Пам'ятай, я завжди поруч. 🌸",
    "Розумничку, маленькі кроки ведуть до великих перемог! ✨",
    "Хочеш сьогодні нове слово англійською? Напиши 'слово'! 📚"
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привіт, Ірусько! Я твоя Робі 🌼")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    if 'слово' in user_message.lower():
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "Ти допомагаєш вивчати англійську. Відповідай лише коротко в такому форматі: слово — переклад. Без пояснень і додаткових фраз."},
                    {"role": "user", "content": "Дай одне нове англійське слово з українським перекладом"}
                ],
                max_tokens=50,
                temperature=0.8
            )
            word_reply = response.choices[0].message.content.strip()
            await update.message.reply_text(f"Слово дня: {word_reply}")
        except Exception as e:
            await update.message.reply_text("Не вдалось отримати нове слово, Ірусько 😔 Спробуй пізніше.")
            print(f"GPT слово error: {e}")
        return

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "Ти ніжна і підтримуюча подруга на ім'я Робі."},
                {"role": "user", "content": user_message}
            ],
            max_tokens=200,
            temperature=0.7
        )
        gpt_reply = response.choices[0].message.content.strip()
        await update.message.reply_text(gpt_reply)

    except Exception as e:
        await update.message.reply_text("Вибач, Ірусько, я щось не зрозуміла. Спробуй ще раз 🥺")
        print(f"GPT error: {e}")
        return

    if 'дякую' in user_message.lower():
        await update.message.reply_text("Завжди з тобою, Рибко! 💖")
    else:
        await update.message.reply_text(random.choice(FRIENDLY_REPLIES))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    file_path = "photo.jpg"
    await photo.download_to_drive(file_path)

    img = Image.open(file_path)
    text = pytesseract.image_to_string(img)

    if text.strip():
        await update.message.reply_text(f"Я знайшла на фото такий текст:\n{text}")
    else:
        await update.message.reply_text("Не змогла розпізнати текст, Рибко 😔 Спробуй ще раз!")

    os.remove(file_path)

async def send_ready_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    with open('robi_ready_voice.mp3', 'rb') as voice:
        await update.message.reply_voice(voice)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('voice', send_ready_voice))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Робі запущена!")
    app.run_polling()
