from app.core.config import settings
from app.main import app
from tortoise.contrib.fastapi import register_tortoise
from tortoise.exceptions import ConfigurationError

TORTOISE_ORM = {
    "connections": {"default": settings.DATABASE_URL},
    "apps": {
        "users_app": {
            "models": ["app.users_app.models", "aerich.models"],
            "default_connection": "default",
        },
        "community_app": {
            "models": ["app.community_app.models"],
            "default_connection": "default",
        },
        "education_app": {
            "models": ["app.education_app.models"],
            "default_connection": "default",
        },
    },
}


async def database_ready() -> bool:
    try:
        register_tortoise(
            app=app,
            config=TORTOISE_ORM,
            generate_schemas=True,
            add_exception_handlers=True,
        )
        return True
    except ConfigurationError as e:
        print(f"🌋 Exception while connecting to database: {e}")
        return False
