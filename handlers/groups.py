from telegram import Update
from telegram.ext import ContextTypes
from database import add_group_db, remove_group_db, list_groups_db

print("💾 Loaded NEW groups.py with -100 support (final fix)")

async def add_group_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["pending_group_name"] = update.message.text.strip()
    await update.message.reply_text(
        "✅ Group name saved!\n\n"
        "Now please do *one* of the following to link the group:\n\n"
        "• 📩 *Forward* a message from the group, OR\n"
        "• 🔗 *Send its @username*, OR\n"
        "• 🆔 *Paste the numeric chat ID* (starts with `-100`)\n\n"
        "_Example: -1001234567890_",
        parse_mode="Markdown"
    )

async def set_group_chat_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = context.user_data.get("pending_group_name")
    if not group_name:
        await update.message.reply_text("❌ Error — send group name first.")
        return

    text = update.message.text.strip()
    chat_id = None

    # 🧩 Detect if user forwarded a message
    if getattr(update.message, "forward_from_chat", None):
        chat_id = str(update.message.forward_from_chat.id)
        print(f"📨 Forward detected: chat_id = {chat_id}")

    # 🧩 Detect @username form
    elif text.startswith("@"):
        chat_id = text
        print(f"📨 Username detected: chat_id = {chat_id}")

    # 🧩 Detect numeric chat ID (like -100xxxxxxxx)
    elif text.startswith("-100") or text.lstrip("-").isdigit():
        chat_id = text
        print(f"📨 Numeric ID detected: chat_id = {chat_id}")

    # 🧩 If nothing matched
    if not chat_id:
        await update.message.reply_text(
            "⚠️ Couldn’t detect chat ID.\n\nPlease forward a message from the group, "
            "send its @username, or paste the numeric chat ID (starts with -100)."
        )
        return

    # ✅ Save to DB
    await add_group_db(group_name, chat_id)
    await update.message.reply_text(
        f"✅ Group *{group_name}* added!\nChat ID: `{chat_id}`",
        parse_mode="Markdown"
    )
    context.user_data.pop("pending_group_name", None)

async def remove_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    group_name = update.message.text.strip()
    ok = await remove_group_db(group_name)

    if ok:
        await update.message.reply_text(f"🗑 Group `{group_name}` removed.", parse_mode="Markdown")
    else:
        await update.message.reply_text("⚠️ Group not found.")

async def list_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    rows = await list_groups_db()
    if not rows:
        await update.message.reply_text("No groups yet.")
        return

    text = "\n".join([f"• *{g[0]}* — `{g[1]}`" for g in rows])
    await update.message.reply_text(text, parse_mode="Markdown")

# 🧩 Register group handlers
def register_handlers(app):
    print("🧩 Registering groups handlers...")

    from telegram.ext import MessageHandler, filters

    # This handler listens for group name and ID inputs from admins
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, set_group_chat_id))
