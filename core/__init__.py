from core.config import settings
from core.database import Base, get_db, engine
from core.redis import redis_client, save_otp, verify_otp
from core.get_current_user import get_current_customer