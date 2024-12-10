from app.core.config import settings
from aredis_om import Field, JsonModel, get_redis_connection

async_redis_connection = get_redis_connection(url=settings.REDIS_URL, decode_responses=True)


async def redis_om_ready() -> bool:
    try:
        await async_redis_connection.ping()
        return True
    except Exception as e:
        print(f"🌋 Failed in redis_om_ready: {e}")
        return False


class RegisterRedisModel(JsonModel):
    code: str = Field(index=True, case_sensitive=False)
    username: str = Field(index=True, case_sensitive=False)
    email: str = Field(index=True, case_sensitive=False)
    password: str = Field(index=True, case_sensitive=False)

    class Meta:
        database = async_redis_connection
