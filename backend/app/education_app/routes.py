import asyncio
import os
import shutil
from typing import Any, AsyncGenerator

import aiofiles
from aiopytesseract import image_to_string
from fastapi import APIRouter, Header, UploadFile, status

education_router = APIRouter()


# ! upload_images
@education_router.post(path="/upload", status_code=status.HTTP_200_OK)
async def upload_images(files: list[UploadFile], content_type: str = Header()):
    print(f"📝 content_type: {content_type}")

    raw_texts: list[str] = []
    sorted_texts = ()

    cwd: str = os.getcwd()
    os.makedirs(os.path.join(cwd, "flutter_images"), exist_ok=True)
    temp_file_path = os.path.join(cwd, "flutter_images")

    try:
        for file in files:
            file_path = os.path.join(temp_file_path, file.filename)
            async with aiofiles.open(file_path, mode="wb") as f:
                while chunk := await file.read(1024 * 1024):
                    await f.write(chunk)
    except Exception as e:
        print(f"🌋 Exception while writing file: {e}")

    try:
        file_paths = os.listdir(temp_file_path)
        print(f"📝 file_paths: {file_paths}")

        for file_path in file_paths:
            extracted_text = await image_to_string(f"{temp_file_path}/{file_path}")
            raw_texts.append(extracted_text)
            for text in raw_texts:
                lines = text.split("\n")
                word = lines[0].strip()
                if word:
                    sorted_texts = sorted_texts + (word,)

        shutil.rmtree(temp_file_path)

        return sorted_texts

    except Exception as e:
        print(f"🌋 Exception while reading file: {e}")


async def iterate_face_response() -> AsyncGenerator[str, Any]:
    yield "1"
    await asyncio.sleep(2)
    yield "2"
