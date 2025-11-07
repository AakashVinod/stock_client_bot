
# 💼 Business Client Telegram Bot

This bot is designed for businesses, trading services, or private communities that need to verify clients and automatically add them to specific Telegram groups — safely and efficiently.
It’s built to be modular, admin-controlled, and automated — everything managed right inside Telegram itself

A modular Telegram client management bot built with Python and python-telegram-bot.
Deployed on Render with an integrated Flask keep-alive server, and kept online 24/7 using UptimeRobot HTTP monitoring.

## 🚀 Features

- 🔐 1️⃣ Client Verification System
💬 When a user sends their Client ID to the bot:
The bot checks if that ID exists in the database.
Each client ID is mapped to a specific group (for example: Premium, Limitless, Gold Members, etc.)
If valid, the bot generates a unique one-time invite link for that group.
The client can use that link to join the private Telegram group instantly.
⚙️ If the Client ID is invalid, the bot politely rejects it:
❌ Invalid Client ID. Please contact support.
✅ This system ensures only verified clients can access exclusive or paid groups — no manual checking required.

- 🧩 2️⃣ Powerful Admin Panel (via /panel command)
Only admin users can access this menu.
When the admin types /panel, an interactive inline menu appears with buttons like:

➕ Add Client
📦 Bulk Clients
🏷 Groups
📋 List Clients
🗑 Remove Client
❌ Exit

Each button performs a different management action — all handled via Telegram inline buttons, no typing commands manually.

💡 Features inside panel:
➕ Add Client → Add a single client ID and assign it to a group.
📦 Bulk Clients → Add multiple client IDs from a text file or list.
🏷 Groups → Add, list, or remove Telegram groups from the system.
📋 List Clients → View all current clients and which group they belong to.
🗑 Remove Client → Remove a specific client from the database.
It’s like a mini control dashboard — directly in Telegram 👑

-💬 3️⃣ Group Management
Admins can easily add or manage Telegram groups that clients will join.
When you add a group:
You give it a name (example: “Limitless”).
Then forward a message from that group OR send its @username OR paste its chat ID (e.g., -100123456454890).
The bot stores it in the database and links clients automatically.
You can also list or remove groups anytime from /panel.
This means one bot can handle multiple client groups, each with unique invite links and client access lists.

-🔗 4️⃣ One-Time Invite Links
When a client verifies successfully:
The bot generates a unique, one-time, time-limited invite link for the correct group.
After use, it becomes invalid.
Prevents link sharing or unauthorized access.

-💾 5️⃣ SQLite Database Integration
All clients and groups are stored locally in an SQLite database:
Fast, lightweight, and zero setup required.
Fully async (via aiosqlite) — perfect for cloud hosting.
Keeps track of all Client IDs, Groups, and their mappings.
You can back up or view the database file anytime (clients_v2.db).

-🌐 6️⃣ 24/7 Cloud Hosting on Render
The bot runs continuously on Render Cloud, using:
A Flask web server to keep it alive (so Render doesn’t suspend it).
Telegram bot polling running asynchronously.
Automatic redeploy when you push new updates to GitHub.
That means your bot:
✅ Never sleeps
✅ Restarts automatically after crashes
✅ Runs fully free

-🧠 8️⃣ Logging & Debugging Ready
All major events are logged:
Client verification attempts
Invite link generation
Admin actions
You can check everything in Render logs or your local console — helps with debugging or monitoring.

-🔒 9️⃣ Security Features
Only admins (via Telegram user ID) can manage clients or groups.
Environment variable for BOT_TOKEN (hidden on GitHub).
Invite links expire after use — no public sharing.
Database operations are safe and isolated.

-🌟 10️⃣ Real-World Use Case
Perfect for:
💼 Trading or stock advisory services (like your channel!)
🧑‍🏫 Online course access control
💎 Premium Telegram community management
🔒 Private group verification for paid users

Basically, any system where you need automated group access based on user verification.

##🌍 Deployment Setup

The bot is hosted on Render using a free web service.
Since Render’s free instances automatically “sleep” after ~15 minutes of inactivity, a Flask keep-alive endpoint (/) is added.
This endpoint returns a simple response so the service can receive periodic pings.

##💡 24/7 Uptime with UptimeRobot

To prevent the Render instance from going idle:
The public Flask route (https://your-app-name.onrender.com/) is monitored by UptimeRobot every few minutes.
UptimeRobot continuously pings the app to keep the Render container active.
As a result, the Telegram bot process inside the same container remains alive indefinitely.

## ⚙️ Tech Stack

Python 3.11+
python-telegram-bot v21
Flask (for keep-alive)
SQLite3
Render (Hosting)
UptimeRobot (Ping Monitoring)

# 👨‍💻 Author

Akash Vinod
💼 [Akash Vinod](https://github.com/AakashVinod)
🧠 Originally developed this Telegram Client Bot with Flask keep-alive and Render deployment
🕓 Keeping it alive 24/7 via UptimeRobot integration
