import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("TELEGRAM_TOKEN")
DEEPSEEK = os.getenv("DEEPSEEK_API_KEY")
OWNER = int(os.getenv("OWNER_ID"))

memory = {}

def deepseek_chat(user_id, prompt):

    history = memory.get(user_id, [])

    messages = history + [{"role":"user","content":prompt}]

    url = "https://api.deepseek.com/chat/completions"

    headers = {
        "Authorization": f"Bearer {DEEPSEEK}",
        "Content-Type": "application/json"
    }

    data = {
        "model":"deepseek-chat",
        "messages":messages
    }

    r = requests.post(url, headers=headers, json=data)

    if r.status_code != 200:
        return "API hata"

    cevap = r.json()["choices"][0]["message"]["content"]

    history.append({"role":"user","content":prompt})
    history.append({"role":"assistant","content":cevap})

    memory[user_id] = history[-10:]

    return cevap


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        "🤖 AI Bot hazır!\n\n"
        "Mesaj yaz → cevap vereyim\n"
        "/reset → hafızayı temizler"
    )


async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):

    uid = update.message.from_user.id

    if uid in memory:
        del memory[uid]

    await update.message.reply_text("Memory temizlendi 🧠")


async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user = update.message.from_user.id

    if user != OWNER:
        return

    msg = update.message.text

    await update.message.reply_text("🤔 düşünüyorum...")

    cevap = deepseek_chat(user, msg)

    if len(cevap) > 4000:
        for i in range(0, len(cevap), 4000):
            await update.message.reply_text(cevap[i:i+4000])
    else:
        await update.message.reply_text(cevap)


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

app.run_polling()
