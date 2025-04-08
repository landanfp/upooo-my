# Don't Remove Credit Tg - @VJ_Botz
# Subscribe YouTube Channel For Amazing Bot https://youtube.com/@Tech_VJ
# Ask Doubt on telegram @KingVJ01

from config import Config
from database.database import (
    get_user, update_user, reset_daily_usage, is_admin, get_user_plan,
    add_plan_to_user, can_upload, update_usage, get_wait_time,
    create_vip_code, use_vip_code
)

techvj = Database(Config.TECH_VJ_DATABASE_URL, Config.TECH_VJ_SESSION_NAME)
