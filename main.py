import os
import asyncio
import logging
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)
from handlers import admin_panel, client_verify, bulk_import, groups
from config import BOT_TOKEN  # ✅ securely imported

# 🪟 Fix for Windows async loops
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

if __name__ == "__main__":
    print("🤖 Bot running (modular v2)...")
    app.run_polling(poll_interval=2.0, timeout=5.0)
