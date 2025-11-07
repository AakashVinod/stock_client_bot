from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database import add_client_db, remove_client_db, list_clients_db, list_groups_db, add_group_db, remove_group_db
from handlers import groups, bulk_import


# ✅ Check admin permission
def is_admin(uid):
    return uid in ADMIN_IDS


# 🧩 Helper — reopen admin panel
async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➕ Add Client", callback_data="add_single")],
        [InlineKeyboardButton("📦 Bulk Clients", callback_data="bulk")],
        [InlineKeyboardButton("🏷 Groups", callback_data="groups")],
        [InlineKeyboardButton("📋 List Clients", callback_data="list")],
        [InlineKeyboardButton("🗑 Remove Client", callback_data="rm")],
        [InlineKeyboardButton("❌ Exit", callback_data="exit")]
    ]
    try:
        if update.callback_query:
            await update.callback_query.message.reply_text("Admin Panel", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text("Admin Panel", reply_markup=InlineKeyboardMarkup(keyboard))
    except Exception as e:
        print("⚠️ show_panel error:", e)


# 🏁 /panel command
async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⛔ Not allowed.")
        return
    await show_panel(update, context)


# 🧠 Button handler
async def admin_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    uid = q.from_user.id
    if not is_admin(uid):
        await q.edit_message_text("⛔ Access denied.")
        return

    # ➕ Single client add
    if data == "add_single":
        await q.edit_message_text("Send Client ID:")
        context.user_data["state"] = "add_single"
        return

    # 📦 Bulk import menu
    if data == "bulk":
        keyboard = [
            [InlineKeyboardButton("📋 Paste IDs", callback_data="paste")],
            [InlineKeyboardButton("📂 Upload File", callback_data="file")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]
        await q.edit_message_text("Bulk Import:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # 🏷 Group management
    if data == "groups":
        keyboard = [
            [InlineKeyboardButton("➕ Add Group", callback_data="g_add")],
            [InlineKeyboardButton("📋 List Groups", callback_data="g_list")],
            [InlineKeyboardButton("🗑 Remove Group", callback_data="g_rm")],
            [InlineKeyboardButton("⬅️ Back", callback_data="back")]
        ]
        await q.edit_message_text("Group Menu", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # 📋 List clients
    if data == "list":
        rows = await list_clients_db()
        msg = "\n".join([f"{r[0]} — {r[1]}" for r in rows]) or "No clients found."
        await q.edit_message_text(msg)
        await show_panel(update, context)
        return

    # 🗑 Remove client
    if data == "rm":
        await q.edit_message_text("Send Client ID to remove:")
        context.user_data["state"] = "remove_client"
        return

    # Exit or back
    if data == "exit" or data == "back":
        await q.edit_message_text("Exited ✅")
        context.user_data.clear()
        return

    # ➕ Add group
    if data == "g_add":
        await q.edit_message_text("Send new group name:")
        context.user_data["state"] = "add_group_name"
        return

    # 📋 List groups
    if data == "g_list":
        await groups.list_groups(q, context)
        await show_panel(update, context)
        return

    # 🗑 Remove group
    if data == "g_rm":
        await q.edit_message_text("Send group name to remove:")
        context.user_data["state"] = "remove_group"
        return

    # ✅ Assign client to group
    if data.startswith("addto_"):
        group = data.split("_", 1)[1]
        cid = context.user_data.get("pending_client_id")
        if not cid:
            await q.edit_message_text("⚠️ No client ID found. Try again.")
            await show_panel(update, context)
            return

        await add_client_db(cid, group, q.from_user.id)
        await q.edit_message_text(f"✅ Client `{cid}` added to group *{group}*.", parse_mode="Markdown")
        context.user_data.clear()
        await show_panel(update, context)
        return


# 💬 Message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    state = context.user_data.get("state")

    # 🟢 ADD GROUP NAME
    if state == "add_group_name":
        context.user_data["pending_group_name"] = text
        context.user_data["state"] = "await_chat_id"
        await update.message.reply_text(
            "✅ Group name saved!\n\n"
            "Now please do *one* of the following to link the group:\n\n"
            "• 📩 *Forward* a message from the group, OR\n"
            "• 🔗 *Send its @username*, OR\n"
            "• 🆔 *Paste the numeric chat ID* (starts with `-100`)\n\n"
            "_Example: -1001234567890_",
            parse_mode="Markdown"
        )
        return

    # 🟢 ADD GROUP CHAT ID (delegate to groups.py)
    if state == "await_chat_id":
        from handlers import groups
        await groups.set_group_chat_id(update, context)
        return


    # 🟢 REMOVE GROUP
    if state == "remove_group":
        from database import remove_group_db
        ok = await remove_group_db(text)
        if ok:
            await update.message.reply_text(
                f"🗑 Group *{text}* removed successfully!", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"⚠️ Group *{text}* not found in database.", parse_mode="Markdown"
            )
        context.user_data.clear()
        await show_panel(update, context)
        return

    # 🟢 ADD SINGLE CLIENT
    if state == "add_single":
        client_id = text
        context.user_data["pending_client_id"] = client_id

        groups_list = await list_groups_db()
        if not groups_list:
            await update.message.reply_text("⚠️ No groups found. Add one first.")
            context.user_data.clear()
            await show_panel(update, context)
            return

        keyboard = [
            [InlineKeyboardButton(g[0], callback_data=f"addto_{g[0]}")] for g in groups_list
        ]
        await update.message.reply_text(
            f"Client ID: `{client_id}`\nSelect group to assign:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        context.user_data["state"] = "await_group_choice"
        return

    # 🟢 REMOVE CLIENT
    if state == "remove_client":
        from database import remove_client_db
        ok = await remove_client_db(text)
        if ok:
            await update.message.reply_text(
                f"🗑 Client `{text}` removed successfully!", parse_mode="Markdown"
            )
        else:
            await update.message.reply_text(
                f"⚠️ Client `{text}` not found.", parse_mode="Markdown"
            )
        context.user_data.clear()
        await show_panel(update, context)
        return

    # 🟡 DEFAULT CASE (no active state)
    else:
        await update.message.reply_text("⚠️ Please use /panel to select an action.")
        return

    # 🧩 Register admin panel handlers
def register_handlers(app):
    print("🧩 Registering admin_panel handlers...")

    from telegram.ext import CommandHandler, MessageHandler, CallbackQueryHandler, filters

    # Command for opening admin panel
    app.add_handler(CommandHandler("panel", panel))

    # Handle button clicks (callback queries)
    app.add_handler(CallbackQueryHandler(admin_router))

    # Handle text inputs (client IDs, group names, etc.)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))


