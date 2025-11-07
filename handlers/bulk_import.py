import csv, io
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import add_client_db, list_groups_db

async def bulk_paste(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw = update.message.text.replace(",", "\n")
    ids = [x.strip() for x in raw.splitlines() if x.strip()]
    context.user_data["bulk_ids"] = ids

    groups = await list_groups_db()
    keyboard = [[InlineKeyboardButton(g[0], callback_data=f"bulk_{g[0]}")] for g in groups]

    await update.message.reply_text(
        f"Found {len(ids)} IDs.\nSelect group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def bulk_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    content = (await file.download_as_bytearray()).decode()

    ids = []
    try:
        reader = csv.reader(io.StringIO(content))
        for row in reader:
            ids.append(row[0])
    except:
        ids = content.replace(",", "\n").splitlines()

    ids = [x.strip() for x in ids if x.strip()]
    context.user_data["bulk_ids"] = ids

    groups = await list_groups_db()
    keyboard = [[InlineKeyboardButton(g[0], callback_data=f"bulk_{g[0]}")] for g in groups]

    await update.message.reply_text(
        f"Imported {len(ids)} IDs.\nSelect group:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def assign_bulk(update: Update, context: ContextTypes.DEFAULT_TYPE, group):
    ids = context.user_data["bulk_ids"]
    for cid in ids:
        await add_client_db(cid, group, update.effective_user.id)

    await update.callback_query.edit_message_text(
        f"✅ Added {len(ids)} clients to *{group}*",
        parse_mode="Markdown"
    )
    context.user_data.pop("bulk_ids", None)

def register_handlers(app):
    from telegram.ext import MessageHandler, filters
    app.add_handler(MessageHandler(filters.Document.ALL, bulk_file))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bulk_paste))
