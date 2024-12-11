from app.core.my_database import tortoise_ready, TORTOISE_ORM
from app.core.my_middleware import LoggingMiddleware
from app.core.my_minio import minio_ready
from app.core.my_redis import redis_om_ready
from app.education_app.routes import education_router
from app.users_app.routes import users_router
from fastapi import FastAPI, Request
from tortoise.contrib.fastapi import register_tortoise


app: FastAPI = FastAPI()
app.add_middleware(middleware_class=LoggingMiddleware)

register_tortoise(app=app, config=TORTOISE_ORM, generate_schemas=True, add_exception_handlers=True)

app.include_router(router=users_router, prefix="/users", tags=["users"])
app.include_router(router=education_router, prefix="/education", tags=["education"])


@app.get(path="/", tags=["root"])
async def root():
    return {"message": "🚀"}


@app.get(path="/health", tags=["check health"])
async def health_check():
    return {"status": "healthy"}


@app.get(path="/ready", tags=["check ready"])
async def ready_check():
    data = {"tortoise": "🌋", "redis": "🌋", "minio": "🌋"}
    if await tortoise_ready():
        data["tortoise"] = "🚀"
    if await redis_om_ready():
        data["redis"] = "🚀"
    if await minio_ready():
        data["minio"] = "🚀"
    return data

@app.get(path="/metrics", tags=["monitoring"])
async def metrics():
    # get metrics from logs and send to user
    return {}
