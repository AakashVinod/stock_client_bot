import os
import asyncio
import logging
import threading
from flask import Flask
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from handlers import admin_panel, client_verify, bulk_import, groups
from config import BOT_TOKEN  # ✅ securely imported

# 🪟 Fix for Windows async loops (only on Windows)
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# 🌐 Prevent HTTPS blocking (Windows workaround)
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["NO_PROXY"] = "api.telegram.org"

# 🧾 Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# 🔒 Safety check: warn if token not found
if not BOT_TOKEN:
    raise ValueError("❌ BOT_TOKEN not found! Please set it as an environment variable.")

# ⚙️ Build the bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

# 🧩 Register handlers
client_verify.register_handlers(app)
admin_panel.register_handlers(app)
bulk_import.register_handlers(app)
groups.register_handlers(app)

print("✅ Invite link system loaded successfully")

# 🌍 Flask keep-alive server
flask_app = Flask(__name__)

@flask_app.route('/')
def home():
    return "🤖 Telegram Bot is alive!", 200

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

# 🚀 Start Flask server and bot
if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    print("🤖 Bot running (modular v2)...")
    app.run_polling(poll_interval=2.0, timeout=5.0)
