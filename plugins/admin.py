# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from pyrogram import Client as Tech_VJ
from pyrogram import filters, enums
from config import Config
from database.access import techvj
from plugins.buttons import *

@Tech_VJ.on_message(filters.private & filters.command('total'))
async def sts(c, m):
    if m.from_user.id != Config.TECH_VJ_OWNER_ID:
        return 
    total_users = await techvj.total_users_count()
    await m.reply_text(text=f"Total user(s) {total_users}", quote=True)


@Tech_VJ.on_message(filters.private & filters.command("search"))
async def serc(bot, update):

      await bot.send_message(chat_id=update.chat.id, text="🔍 TORRENT SEARCH", 
      parse_mode=enums.ParseMode.HTML, reply_markup=Button.BUTTONS01)


# --- Moved from handlers/admins.py ---
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from config import ADMINS
from database.database import users_col, PLAN_DETAILS
from datetime import datetime, timedelta

@Client.on_message(filters.command("addpro") & filters.user(ADMINS))
async def add_pro(bot, message):
    if len(message.command) < 2:
        return await message.reply("لطفاً آیدی عددی کاربر را وارد کنید.")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply("آیدی نامعتبر است.")

    keyboard = InlineKeyboardMarkup(
        [[
            InlineKeyboardButton("نقره‌ای", callback_data=f"setplan_silver_{user_id}"),
            InlineKeyboardButton("طلایی", callback_data=f"setplan_gold_{user_id}"),
            InlineKeyboardButton("الماسی", callback_data=f"setplan_diamond_{user_id}")
        ]]
    )
    await message.reply("یکی از پلن‌های زیر را انتخاب کنید:", reply_markup=keyboard)

@Client.on_callback_query(filters.regex("setplan_") & filters.user(ADMINS))
async def set_plan(bot, query):
    parts = query.data.split("_")
    if len(parts) != 3:
        return await query.answer("خطا")

    plan, user_id = parts[1], int(parts[2])
    duration = PLAN_DETAILS[plan]["duration"]
    expiry = datetime.utcnow() + timedelta(days=duration) if duration else None

    users_col.update_one({"_id": user_id}, {
        "$set": {
            "plan": plan,
            "plan_expiry": expiry,
            "daily_usage": 0
        }
    }, upsert=True)
    await query.message.edit_text(f"پلن {plan} برای کاربر {user_id} فعال شد.")

@Client.on_message(filters.command("remove_pro") & filters.user(ADMINS))
async def remove_pro(bot, message):
    if len(message.command) < 2:
        return await message.reply("لطفاً آیدی عددی کاربر را وارد کنید.")

    try:
        user_id = int(message.command[1])
    except ValueError:
        return await message.reply("آیدی نامعتبر است.")

    users_col.update_one({"_id": user_id}, {
        "$set": {
            "plan": "free",
            "plan_expiry": None,
            "daily_usage": 0
        }
    })
    await message.reply(f"پلن کاربر {user_id} به رایگان تغییر یافت.")


@Client.on_message(filters.command("my_plan"))
async def my_plan(bot, message):
    from datetime import datetime
    from database.database import PLAN_DETAILS

    user_id = message.from_user.id
    user = users_col.find_one({"_id": user_id}) or {}
    plan = user.get("plan", "free")
    usage = user.get("daily_usage", 0)
    expiry = user.get("plan_expiry")
    now = datetime.utcnow()

    plan_info = PLAN_DETAILS.get(plan, {})
    total = plan_info.get("daily_limit", 0)
    remaining = max(0, total - usage)
    expire_text = expiry.strftime("%Y-%m-%d %H:%M:%S") if expiry else "نامحدود"
    days_left = (expiry - now).days if expiry else "نامحدود"

    percent = usage / total if total > 0 else 0
    filled = int(percent * 10)
    empty = 10 - filled
    bar = "█" * filled + "─" * empty

    text = f"""👤 نام: {message.from_user.first_name}
🆔 آیدی: `{user_id}`
💎 پلن فعلی: {plan}
📦 حجم پلن: {round(total / (1024**3), 2)} GB
✅ استفاده شده: {round(usage / (1024**3), 2)} GB
🗃️ باقیمانده: {round(remaining / (1024**3), 2)} GB
⏳ پایان پلن: {expire_text}
📆 روز باقی‌مانده: {days_left}
📊 میزان استفاده:
[{bar}] {int(percent * 100)}%
"""
    await message.reply(text, quote=True)