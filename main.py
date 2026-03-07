import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
OWNER = int(os.getenv("OWNER_ID"))

def deepseek_chat(prompt):

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    try:
        r = requests.post(url, headers=headers, json=data, timeout=30)

        if r.status_code != 200:
            return f"API Hata: {r.text}"

        return r.json()["choices"][0]["message"]["content"]

    except Exception as e:
        return f"Hata: {str(e)}"


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 AI Bot hazır!")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.message.from_user.id != OWNER:
        return

    msg = update.message.text

    await update.message.reply_text("🤔 düşünüyorum...")

    cevap = deepseek_chat(msg)

    if len(cevap) > 4000:
        for i in range(0, len(cevap), 4000):
            await update.message.reply_text(cevap[i:i+4000])
    else:
        await update.message.reply_text(cevap)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
