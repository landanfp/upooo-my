import json
import os
from datetime import datetime, timedelta
from helper_funcs.logger import logger

DB_FILE = "database/users.json"

DEFAULT_PLAN = {
    "name": "free",
    "daily_limit": 2 * 1024**3,  # 2GB
    "max_file_size": 1024**3,   # 1GB
    "cooldown": 0,
    "expire": None
}


def load_data():
    if not os.path.exists(DB_FILE):
        os.makedirs(os.path.dirname(DB_FILE), exist_ok=True)
        with open(DB_FILE, "w") as f:
            json.dump({}, f)
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return {}


def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_user(user_id):
    data = load_data()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "plan": DEFAULT_PLAN,
            "used_today": 0,
            "last_reset": str(datetime.utcnow().date())
        }
        save_data(data)
    return data[user_id]


def update_user(user_id, user_data):
    data = load_data()
    data[str(user_id)] = user_data
    save_data(data)


def reset_daily_usage_if_needed(user_id):
    user = get_user(user_id)
    today = str(datetime.utcnow().date())
    if user.get("last_reset") != today:
        user["used_today"] = 0
        user["last_reset"] = today
        update_user(user_id, user)


def get_user_plan(user_id):
    reset_daily_usage_if_needed(user_id)
    return get_user(user_id).get("plan", DEFAULT_PLAN)


def set_user_plan(user_id, plan_name, daily_limit, max_file_size, cooldown=0, duration_days=None):
    expire = None
    if duration_days:
        expire = str(datetime.utcnow() + timedelta(days=duration_days))

    user = get_user(user_id)
    user["plan"] = {
        "name": plan_name,
        "daily_limit": daily_limit,
        "max_file_size": max_file_size,
        "cooldown": cooldown,
        "expire": expire
    }
    update_user(user_id, user)


def add_usage(user_id, amount):
    reset_daily_usage_if_needed(user_id)
    user = get_user(user_id)
    user["used_today"] += amount
    update_user(user_id, user)


def get_used_today(user_id):
    reset_daily_usage_if_needed(user_id)
    return get_user(user_id).get("used_today", 0)


def is_plan_expired(user_id):
    plan = get_user_plan(user_id)
    expire = plan.get("expire")
    if expire:
        return datetime.utcnow() > datetime.fromisoformat(expire)
    return False


def downgrade_to_free_if_expired(user_id):
    if is_plan_expired(user_id):
        set_user_plan(user_id, **DEFAULT_PLAN)


def add_plan_to_user(user_id, plan_name, daily_limit, max_file_size, cooldown, duration_days):
    set_user_plan(user_id, plan_name, daily_limit, max_file_size, cooldown, duration_days)
    logger.info(f"User {user_id} upgraded to plan {plan_name} for {duration_days} days.")
