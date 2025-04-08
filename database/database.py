from datetime import datetime, timedelta
from pymongo import MongoClient
import random
import string
import os

MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
client = MongoClient(MONGO_URL)
db = client["vjupbot"]
users_collection = db["users"]
vip_codes_collection = db["vip_codes"]

plans = {
    "free": {
        "daily_limit": 1 * 1024 * 1024 * 1024,
        "wait_time": 180,
        "max_file_size": 100 * 1024 * 1024,
        "duration_days": None,
    },
    "silver": {
        "daily_limit": 5 * 1024 * 1024 * 1024,
        "wait_time": 30,
        "max_file_size": None,
        "duration_days": 30,
    },
    "gold": {
        "daily_limit": 10 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "max_file_size": None,
        "duration_days": 30,
    },
    "diamond": {
        "daily_limit": 30 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "max_file_size": None,
        "duration_days": 30,
    },
    "gift": {
        "daily_limit": 5 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "max_file_size": None,
        "duration_days": 7,
    },
    "vip": {
        "daily_limit": 5 * 1024 * 1024 * 1024,
        "wait_time": 0,
        "max_file_size": None,
        "duration_days": 15,
    }
}


def get_user(user_id):
    user = users_collection.find_one({"user_id": user_id})
    if not user:
        users_collection.insert_one({
            "user_id": user_id,
            "plan": "free",
            "plan_start": None,
            "used_today": 0,
            "last_upload": None,
        })
        return get_user(user_id)
    return user


def update_user(user_id, data: dict):
    users_collection.update_one({"user_id": user_id}, {"$set": data})


def reset_daily_usage():
    users_collection.update_many({}, {"$set": {"used_today": 0}})


def is_admin(user_id):
    return str(user_id) in os.environ.get("ADMINS", "").split()


def get_user_plan(user_id):
    user = get_user(user_id)
    plan = user.get("plan", "free")
    plan_info = plans.get(plan, plans["free"])

    # Check expiration
    if plan_info["duration_days"] and user.get("plan_start"):
        expire_date = user["plan_start"] + timedelta(days=plan_info["duration_days"])
        if datetime.utcnow() > expire_date:
            update_user(user_id, {
                "plan": "free",
                "plan_start": None
            })
            return plans["free"], "free"
    return plan_info, plan


def add_plan_to_user(user_id, plan_key):
    now = datetime.utcnow()
    update_user(user_id, {
        "plan": plan_key,
        "plan_start": now,
        "used_today": 0
    })


def can_upload(user_id, file_size):
    user = get_user(user_id)
    plan_info, plan_name = get_user_plan(user_id)

    max_file_size = plan_info["max_file_size"]
    if max_file_size and file_size > max_file_size:
        return False, f"حجم فایل بیشتر از حد مجاز پلن {plan_name} است."

    today_used = user.get("used_today", 0)
    if today_used + file_size > plan_info["daily_limit"]:
        return False, f"سقف مصرف روزانه پلن {plan_name} تمام شده است."

    return True, None


def update_usage(user_id, file_size):
    user = get_user(user_id)
    today_used = user.get("used_today", 0)
    users_collection.update_one(
        {"user_id": user_id},
        {"$set": {"used_today": today_used + file_size, "last_upload": datetime.utcnow()}}
    )


def get_wait_time(user_id):
    user = get_user(user_id)
    plan_info, _ = get_user_plan(user_id)
    wait_time = plan_info["wait_time"]
    last_upload = user.get("last_upload")
    if not last_upload:
        return 0
    elapsed = (datetime.utcnow() - last_upload).total_seconds()
    remaining = wait_time - elapsed
    return max(0, remaining)


def create_vip_code():
    code = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
    vip_codes_collection.insert_one({"code": code, "used": False})
    return code


def use_vip_code(user_id, code):
    code_data = vip_codes_collection.find_one({"code": code, "used": False})
    if not code_data:
        return False
    vip_codes_collection.update_one({"code": code}, {"$set": {"used": True}})
    add_plan_to_user(user_id, "vip")
    return True
