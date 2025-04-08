from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import add_plan_to_user, get_user_plan

@Client.on_message(filters.command("hadie") & filters.private)
async def activate_gift_plan(client, message: Message):
    user_id = message.from_user.id
    plan = await get_user_plan(user_id)
    if plan["name"] != "free":
        return await message.reply("فقط کاربران پلن رایگان می‌توانند از هدیه استفاده کنند.")

    await add_plan_to_user(user_id, "gift", daily_limit=5 * 1024**3, wait_time=0, duration_days=7)
    await message.reply("پلن هدیه برای شما فعال شد. مدت زمان: ۷ روز | حجم روزانه: ۵ گیگ | بدون محدودیت حجم فایل")