from app.core.database import database_ready
from app.core.minio_client import minio_ready
from app.core.redis_om import redis_om_ready
from app.education_app.routes import education_router
from app.users_app.routes import users_router
from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()

app.include_router(router=users_router, prefix="/users", tags=["users"])
app.include_router(router=education_router, prefix="/education", tags=["education"])


@app.get(path="/", tags=["check health"])
async def health_check():
    is_database_ready = await database_ready()
    is_minio_ready = await minio_ready()
    is_redis_om_ready = await redis_om_ready()

    if is_database_ready and is_minio_ready and is_redis_om_ready:
        return {"status": "healthy"}
    else:
        return {"status": "unhealthy"}

Instrumentator().instrument(app).expose(app)
