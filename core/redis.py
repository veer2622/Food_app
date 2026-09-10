import redis
from core.config import settings



redis_client=redis.Redis(host=settings.REDIS_HOST,
                         port=settings.REDIS_PORT,
                         db=settings.REDIS_DB,
                         decode_responses=True
                         )

try:
    print(redis_client.ping())
except Exception as e:
    print("Redis error:", e)
    
def save_otp(email: str, otp: str):
    key = f"otp:{email}"

    redis_client.set(
        key,
        otp,
        ex=600   # 10 minutes
    )


def verify_otp(email: str, sent_otp: str):
    key = f"otp:{email}"

    otp = redis_client.get(key)

    if otp == sent_otp:
        redis_client.delete(key)
        return True

    return False