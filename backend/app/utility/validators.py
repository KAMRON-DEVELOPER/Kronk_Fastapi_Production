# import random
# import string
# from io import BytesIO
# from typing import Optional
#
# import aiohttp
# from modern_colorthief import get_color
# from PIL import Image
#
# from app.core.config import settings
#
#
# async def get_dominant_color(path=None, object_key=None, image_url=None):
#     print(f"PATH >> {path}, OBJECT_KEY >> {object_key}, IMAGE_URL >> {image_url}")
#     try:
#         dominant_color = None
#         if object_key or image_url:
#             image_data = await download_image(object_key=object_key, image_url=image_url)
#             image_bytes = await prepare_image_data(image_data=image_data)
#
#             if image_bytes:
#                 dominant_color_rgb = await get_color(image_bytes, quality=1)
#                 if dominant_color_rgb:
#                     dominant_color = "#{:02x}{:02x}{:02x}".format(*dominant_color_rgb)
#         elif path:
#             print("path >>>", path)
#             dominant_color_rgb = await get_color(path, quality=1)
#             print("dominant_color_rgb >>>", dominant_color_rgb)
#             if dominant_color_rgb:
#                 dominant_color = "#{:02x}{:02x}{:02x}".format(*dominant_color_rgb)
#         return dominant_color
#     except Exception as e:
#         print(f"Error getting dominant color: {e}")
#
#
# async def download_image(image_url=None):
#     if image_url:
#         try:
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(image_url) as response:
#                     response.raise_for_status()
#                     image_data: bytes = await response.read()
#                     return image_data
#         except Exception as e:
#             print(f"🥶 Error downloading image from URL: {e}")
#             return None
#
#
# async def prepare_image_data(image_data: BytesIO) -> Optional[BytesIO]:
#     try:
#         pil_image = Image.open(fp=image_data)
#         pil_image.verify()  # Verify image validity
#         pil_image = Image.open(fp=image_data)  # Re-open to manipulate
#
#         if pil_image.mode != "RGB":
#             pil_image = pil_image.convert("RGB")
#
#         output_image = BytesIO()
#         pil_image.save(output_image, format="PNG")
#         output_image.seek(0)
#
#         return output_image
#     except Exception as e:
#         print(f"🌋 Exception in prepare_image_data: {e}")
#         return None
#
#
# async def upload_image_to_storage(object_key: str, image_data: BytesIO) -> None:
#     image_data.seek(0)
#
#     try:
#         with open(f"{settings.MEDIA_ROOT}/{object_key}", "wb") as f:
#             f.write(image_data.read())
#     except Exception as e:
#         print(f"🌋 Exception in upload_image_to_storage: {e}")
#
#
# async def user_credential_generator(field: str, populated_field=None, generated_username=None):
#     if field == "username" and populated_field is not None:
#         return await generate_unique_username(populated_field)
#
#     if field == "password":
#         return await generate_password(length=8)
#
#     if field == "avatar" and populated_field is not None:
#         return await generate_avatar_url(populated_field, generated_username)
#
#
# async def generate_unique_username(base_name):
#     username = base_name.lower().replace(" ", "_")
#     # TODO: caching usernames
#     # TODO: check if username is available
#     return username
#
#
# async def generate_password(length=12):
#     characters = string.ascii_letters + string.digits + string.punctuation
#     password = "".join(random.choice(characters) for _ in range(length))
#     return password
#
#
# async def generate_avatar_url(image_url, generated_username):
#     print(f"🚧 IMAGE_URL >> {image_url}, GENERATED_USERNAME >> {generated_username}")
#     image_data = await download_image(image_url=image_url)
#     if image_data:
#         image_bytes = await prepare_image_data(image_data=image_data)
#         if image_bytes:
#             object_key = f"{generated_username}_avatar.jpg"  # generate filename
#             print("4) ��� Object key generated: ", object_key)
#
#             await upload_image_to_storage(image_bytes, f"users/{generated_username}/{object_key}")
#
#             if settings.STORAGE_DESTINATION == "s3":
#                 generated_avatar_url = f"https://{settings.AWS_CUSTOM_DOMAIN}/media/users/{generated_username}/{object_key}"
#             else:
#                 generated_avatar_url = f"{settings.MEDIA_URL}users/{generated_username}/{object_key}"
#             print("5) ��� Avatar URL generated: ", generated_avatar_url)
#             return generated_avatar_url
