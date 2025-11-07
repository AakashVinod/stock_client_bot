import aiosqlite
from config import DB_PATH

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                group_name TEXT UNIQUE,
                chat_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                client_id TEXT PRIMARY KEY,
                group_name TEXT,
                added_by INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.commit()


async def add_group_db(group_name: str, chat_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR IGNORE INTO groups (group_name, chat_id) VALUES (?, ?)",
            (group_name, chat_id)
        )
        await db.commit()


async def update_group_chatid(group_name: str, chat_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE groups SET chat_id = ? WHERE group_name = ?",
            (chat_id, group_name)
        )
        await db.commit()


async def remove_group_db(group_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM groups WHERE group_name = ?", (group_name,))
        await db.commit()
        return cur.rowcount > 0


async def list_groups_db():
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT group_name, chat_id, created_at FROM groups ORDER BY created_at DESC")
        return await cur.fetchall()


async def get_group_chatid(group_name: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT chat_id FROM groups WHERE group_name = ?", (group_name,))
        row = await cur.fetchone()
        return row[0] if row else None


async def add_client_db(client_id: str, group_name: str, added_by: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "INSERT OR REPLACE INTO clients (client_id, group_name, added_by) VALUES (?, ?, ?)",
            (client_id, group_name, added_by)
        )
        await db.commit()


async def remove_client_db(client_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("DELETE FROM clients WHERE client_id = ?", (client_id,))
        await db.commit()
        return cur.rowcount > 0


async def list_clients_db(limit=200):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT client_id, group_name, added_by, added_at FROM clients ORDER BY added_at DESC LIMIT ?", (limit,))
        return await cur.fetchall()


async def get_client_group(client_id: str):
    async with aiosqlite.connect(DB_PATH) as db:
        cur = await db.execute("SELECT group_name FROM clients WHERE client_id = ?", (client_id,))
        row = await cur.fetchone()
        return row[0] if row else None
