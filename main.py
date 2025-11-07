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

# 🧩 Register all handlers
client_verify.register_handlers(app)
admin_panel.register_handlers(app)
bulk_import.register_handlers(app)
groups.register_handlers(app)

print("✅ Invite link system loaded successfully")

# 🌐 Simple Flask web server to keep Render’s web service alive
flask_app = Flask(__name__)

@flask_app.route("/")
def home():
    return "✅ Business Client Bot is running successfully!"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    flask_app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    print("🚀 Starting bot with Flask keep-alive server (Render mode)...")
    
    # Start Flask in a background thread (to prevent blocking the bot)
    threading.Thread(target=run_flask, daemon=True).start()
    
    # Run Telegram bot polling
    app.run_polling(poll_interval=2.0, timeout=5.0)
