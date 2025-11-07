from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters
from database import get_client_group, get_group_chatid
from utils.invite_link import generate_one_time_invite


# 🟢 START COMMAND
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("⚙️ /start command received")
    await update.message.reply_text(
        "👋 Welcome!\n\nPlease send your *Client ID* to verify your access.",
        parse_mode="Markdown"
    )


# 🟢 VERIFY CLIENT ID
async def verify_client(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("📩 Client sent a message to verify")
    client_id = update.message.text.strip()
    print(f"🔍 Checking Client ID: {client_id}")

    try:
        # 🔹 Step 1: Check if client exists in DB
        group = await get_client_group(client_id)
        print(f"📊 Group found for {client_id}: {group}")

        if not group:
            await update.message.reply_text(
                "❌ Invalid Client ID.\nPlease contact your admin for assistance."
            )
            return

        # 🔹 Step 2: Get linked chat ID from group name
        chat_id = await get_group_chatid(group)
        print(f"💬 Chat ID for group '{group}': {chat_id}")

        if not chat_id:
            await update.message.reply_text(
                f"⚠️ Group *{group}* has no linked Chat ID.\nContact admin to fix this.",
                parse_mode="Markdown"
            )
            return

        # 🔹 Step 3: Prepare success message
        msg = f"✅ Verified!\nClient ID: `{client_id}`\nGroup: *{group}*"

        # 🔹 Step 4: Try to generate one-time invite link
        try:
            link = await generate_one_time_invite(context.bot, chat_id)
            print(f"🔗 Generated link: {link}")

            if link:
                msg += f"\n\n👉 [Join your private group]({link})"
            else:
                msg += "\n⚠️ Failed to generate invite link. Ask admin to check permissions."

        except Exception as e:
            print(f"⚠️ Invite link error: {e}")
            msg += f"\n⚠️ Error creating invite link — contact admin."

        # 🔹 Step 5: Send final verification message
        await update.message.reply_text(
            msg,
            parse_mode="Markdown",
            disable_web_page_preview=True
        )
        print("✅ Verification message sent")

    except Exception as e:
        print(f"💥 Exception in verify_client: {e}")
        await update.message.reply_text(
            f"⚠️ Unexpected error while verifying: `{e}`",
            parse_mode="Markdown"
        )


# 🧩 HANDLER REGISTRATION
def register_handlers(app):
    print("🧩 Registering client_verify handlers...")
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, verify_client))
