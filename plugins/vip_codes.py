from pyrogram import Client, filters
from pyrogram.types import Message
from database.database import add_plan_to_user, is_admin, get_user_plan, use_vip_code, create_vip_code
import random, string

@Client.on_message(filters.command("crate_vip") & filters.private)
async def generate_vip_code(client, message: Message):
    if not await is_admin(message.from_user.id):
        return await message.reply("فقط ادمین می‌تواند این دستور را اجرا کند.")
    
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    await create_vip_code(code)
    await message.reply(f"کد VIP ساخته شد:
`{code}`")

@Client.on_message(filters.command("vip") & filters.private)
async def use_code(client, message: Message):
    try:
        code = message.text.split(" ", 1)[1].strip()
    except IndexError:
        return await message.reply("لطفاً کد VIP را وارد کنید.
مثال: /vip ABCD1234")

    user_id = message.from_user.id
    plan = await get_user_plan(user_id)
    if plan["name"] != "free":
        return await message.reply("شما هم‌اکنون در پلن غیررایگان هستید. فقط کاربران رایگان می‌توانند از این کد استفاده کنند.")

    valid = await use_vip_code(code, user_id)
    if not valid:
        return await message.reply("کد نامعتبر است یا قبلاً استفاده شده است.")

    await add_plan_to_user(user_id, "vip", daily_limit=5 * 1024**3, wait_time=0, duration_days=15)
    await message.reply("پلن VIP برای شما فعال شد. اعتبار: ۱۵ روز | حجم روزانه: ۵ گیگ | بدون محدودیت حجم فایل")