from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from gtts import gTTS
import openai
import os
import random

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
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Робі запущена!")
    app.run_polling()
