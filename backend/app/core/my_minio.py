from datetime import timedelta

import aiofiles
from app.core.config import settings
from fastapi import UploadFile
from miniopy_async import Minio

minio_client: Minio = Minio(access_key=settings.MINIO_USER_ACCESS_KEY, secret_key=settings.MINIO_USER_SECRET_KEY, endpoint=settings.MINIO_ENDPOINT, secure=False)


async def minio_ready() -> bool:
    try:
        is_exists_bucket = await minio_client.bucket_exists(bucket_name=settings.MINIO_BUCKET_NAME)
        if not is_exists_bucket:
            await minio_client.make_bucket(bucket_name=settings.MINIO_BUCKET_NAME)
        return True
    except Exception as e:
        print(f"🌋 Failed in check_if_bucket_exists: {e}")
        return False


async def generate_put_presigned_url(object_name: str) -> str:
    try:
        url: str = await minio_client.presigned_put_object(bucket_name=settings.MINIO_BUCKET_NAME, object_name=object_name, expires=timedelta(days=1))
        print(f"🚧 generate_put_presigned_url: {url}")
        return url
    except Exception as e:
        print(f"🌋 Failed in upload_object: {e}")


async def generate_get_presigned_url(object_name: str) -> str:
    try:
        url: str = await minio_client.presigned_get_object(bucket_name=settings.MINIO_BUCKET_NAME, object_name=object_name, expires=timedelta(days=1))
        print(f"🚧 generate_get_presigned_url: {url}")
        return url
    except Exception as e:
        print(f"🌋 Failed in generate_get_presigned_url: {e}")


async def upload_file_to_minio(file: UploadFile, username: str) -> str:
    try:
        # Generate unique object name for MinIO
        object_name = f"users/{username}/{file.filename}"

        # Use aiofiles' TemporaryFile for temporary storage
        async with aiofiles.tempfile.NamedTemporaryFile("wb") as temp_file:
            # Read and write the content of the uploaded file into the temporary file
            await temp_file.write(await file.read())
            await temp_file.flush()

            # Upload the temporary file to MinIO
            await minio_client.fput_object(bucket_name=settings.MINIO_BUCKET_NAME, object_name=object_name, file_path=temp_file.name)

        # Return the object name
        return object_name
    except Exception as e:
        raise ValueError(f"🌋 Failed in upload_file_to_minio: {e}")
