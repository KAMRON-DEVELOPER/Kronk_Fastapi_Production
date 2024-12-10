from app.core.my_database import tortoise_ready
from app.core.my_minio import minio_ready
from app.core.my_redis import redis_om_ready
from app.education_app.routes import education_router
from app.users_app.routes import users_router
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app: FastAPI = FastAPI()

Instrumentator().instrument(app).expose(app)

app.include_router(router=users_router, prefix="/users", tags=["users"])
app.include_router(router=education_router, prefix="/education", tags=["education"])


@app.get(path="/")
async def root():
    return {"message": "🚀"}


@app.get(path="/ready", tags=["check ready"])
async def ready_check():
    data = {"tortoise": "🌋", "minio": "🌋", "redis": "🌋"}
    if await tortoise_ready(app=app):
        data["tortoise"] = "🚀"
    if await minio_ready():
        data["minio"] = "🚀"
    if await redis_om_ready():
        data["redis"] = "🚀"
    return data
