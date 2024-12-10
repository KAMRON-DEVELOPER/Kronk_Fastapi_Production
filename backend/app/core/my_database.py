from app.core.config import settings
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise

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


async def tortoise_ready(app: FastAPI) -> bool:
    try:
        register_tortoise(app=app, config=TORTOISE_ORM, generate_schemas=True, add_exception_handlers=True)
        return True
    except Exception as e:
        print(f"🌋 Failed in tortoise_ready: {e}")
        return False
