# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

import datetime
import motor.motor_asyncio

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.clinton = self._client[database_name]
        self.col = self.clinton.USERS

    def new_user(self, id):
        return dict(id=id, thumbnail=None)


    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def set_thumbnail(self, id, thumbnail):
        await self.col.update_one({'id': id}, {'$set': {'thumbnail': thumbnail}})

    async def get_thumbnail(self, id):
        user = await self.col.find_one({'id': int(id)})
        return user.get('thumbnail', None)



from datetime import datetime, timedelta
from urllib.parse import urlparse

PLAN_DETAILS = {
    "free": {
        "daily_limit": 1 * 1024 * 1024 * 1024,
        "wait_time": 180,
        "duration": None,
        "restricted_domains": ["xvideos.com", "xnxx.com", "pornhub.com"]
    },
    "silver": {
        "daily_limit": 5 * 1024 * 1024 * 1024,
        "wait_time": 30,
        "duration": 30,
        "restricted_domains": []
    },
    "gold": {
        "daily_limit": 10 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "duration": 30,
        "restricted_domains": []
    },
    "diamond": {
        "daily_limit": 30 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "duration": 30,
        "restricted_domains": []
    }
}

def get_user_plan(user_id: int):
    user = users_col.find_one({"_id": user_id})
    if not user:
        users_col.insert_one({
            "_id": user_id,
            "plan": "free",
            "daily_usage": 0,
            "last_upload_time": None,
            "plan_expiry": None
        })
        return "free"
    return user.get("plan", "free")

def can_upload(user_id: int, file_size: int, url: str) -> (bool, str):
    now = datetime.utcnow()
    user = users_col.find_one({"_id": user_id})
    
    if not user:
        get_user_plan(user_id)
        user = users_col.find_one({"_id": user_id})

    plan = user.get("plan", "free")
    details = PLAN_DETAILS[plan]

    expiry = user.get("plan_expiry")
    if expiry and expiry < now:
        users_col.update_one({"_id": user_id}, {
            "$set": {
                "plan": "free",
                "daily_usage": 0,
                "plan_expiry": None
            }
        })
        return False, "پلن شما به پایان رسیده و به پلن رایگان بازگشتید."

    if user.get("daily_usage", 0) + file_size > details["daily_limit"]:
        return False, "شما به حداکثر حجم مجاز روزانه در پلن فعلی رسیده‌اید."

    last = user.get("last_upload_time")
    if last:
        delta = (now - last).total_seconds()
        if delta < details["wait_time"]:
            return False, f"لطفاً {int(details['wait_time'] - delta)} ثانیه دیگر صبر کنید."

    domain = urlparse(url).netloc
    for banned in details["restricted_domains"]:
        if banned in domain:
            return False, "آپلود از این سایت در پلن رایگان مجاز نیست."

    return True, ""

def update_usage(user_id: int, file_size: int):
    users_col.update_one({"_id": user_id}, {
        "$inc": {"daily_usage": file_size},
        "$set": {"last_upload_time": datetime.utcnow()}
    })


# ------------------- VIP Code System -------------------
import datetime

async def create_vip_code(code: str):
    await vip_codes.insert_one({
        "code": code,
        "used": False,
        "used_by": None,
        "created_at": datetime.datetime.utcnow()
    })

async def use_vip_code(code: str, user_id: int) -> bool:
    vip = await vip_codes.find_one({"code": code, "used": False})
    if not vip:
        return False
    await vip_codes.update_one(
        {"code": code},
        {"$set": {"used": True, "used_by": user_id, "used_at": datetime.datetime.utcnow()}}
    )
    return True