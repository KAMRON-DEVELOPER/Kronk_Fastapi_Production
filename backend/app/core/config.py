import os
from datetime import timedelta

from environ import Env
from fastapi_jwt import JwtAccessBearer, JwtRefreshBearer
from pydantic_settings import BaseSettings

env = Env()
BASE_DIR = os.path.dirname(p=os.path.dirname(p=os.path.dirname(p=os.path.abspath(path=__file__))))

DATABASE_URL: str = env.str(var="DATABASE_URL")
REDIS_URL: str = env.str(var="REDIS_URL")

SECRET_KEY: str = env.str(var="SECRET_KEY")
ALGORITHM: str = env.str(var="ALGORITHM")
ACCESS_TOKEN_EXPIRE_IN_MINUTES: int = env.int(var="ACCESS_TOKEN_EXPIRE_IN_MINUTES")
REFRESH_TOKEN_EXPIRE_IN_MINUTES: int = env.int(var="REFRESH_TOKEN_EXPIRE_IN_MINUTES")

CELERY_BROKER_URL: str = env.str(var="CELERY_BROKER_URL")
CELERY_RESULT_BACKEND: str = env.str(var="CELERY_RESULT_BACKEND")

EMAIL_HOST: str = env.str(var="EMAIL_HOST")
EMAIL_PORT: int = env.int(var="EMAIL_PORT")
EMAIL_HOST_USER: str = env.str(var="EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD: str = env.str(var="EMAIL_HOST_PASSWORD")
EMAIL_USE_TLS: bool = env.bool(var="EMAIL_USE_TLS")

MINIO_USER_ACCESS_KEY: str = env.str(var="MINIO_USER_ACCESS_KEY")
MINIO_USER_SECRET_KEY: str = env.str(var="MINIO_USER_SECRET_KEY")
MINIO_ENDPOINT: str = env.str(var="MINIO_ENDPOINT")
MINIO_BUCKET_NAME: str = env.str(var="MINIO_BUCKET_NAME")
MINIO_PUBLIC_URL_OR_IP: str = env.str(var="MINIO_PUBLIC_URL_OR_IP")

jwtAccessBearer = JwtAccessBearer(
    secret_key=SECRET_KEY,
    auto_error=True,
    algorithm=ALGORITHM,
    access_expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_IN_MINUTES),
    refresh_expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_IN_MINUTES),
)
jwtRefreshBearer = JwtRefreshBearer.from_other(jwtAccessBearer)

# ! Messages
wait_for_verification = "Fuck off, wait for verification code"
redis_om_user_creation_error = "Error occurred while creating temporary user"
email_subject = "Verify your email"
email_body = "Your verification code is:"
temporary_token_not_found_in_headers = "Temporary token not found in headers"
code_not_found_in_body = "Code not found in body"
error_while_getting_temporary_user = "Error while getting temporary user"
wrong_verification_code = "Your verification code is wrong"
wrong_temporary_token = "Your temporary token is wrong"
user_is_registering_with_same_email_and_username = "User is registering with same email and username at the same time"
someone_is_registering_with_same_username = "Someone is registering with same username at the same time"
someone_is_registering_with_same_email = "User is registering with same email at the same time"
username_already_exists = "Username already exists"
email_already_exists = "Email already exists"


class Settings(BaseSettings):
    BASE_DIR: str = BASE_DIR
    DATABASE_URL: str = DATABASE_URL
    REDIS_URL: str = REDIS_URL
    jwtAccessBearer: JwtAccessBearer = jwtAccessBearer
    jwtRefreshBearer: JwtRefreshBearer = jwtRefreshBearer  # type: ignore
    CELERY_BROKER_URL: str = CELERY_BROKER_URL
    EMAIL_HOST: str = EMAIL_HOST
    EMAIL_PORT: int = EMAIL_PORT
    EMAIL_HOST_USER: str = EMAIL_HOST_USER
    EMAIL_HOST_PASSWORD: str = EMAIL_HOST_PASSWORD
    EMAIL_USE_TLS: bool = EMAIL_USE_TLS

    MINIO_USER_ACCESS_KEY: str = MINIO_USER_ACCESS_KEY
    MINIO_USER_SECRET_KEY: str = MINIO_USER_SECRET_KEY
    MINIO_ENDPOINT: str = MINIO_ENDPOINT
    MINIO_BUCKET_NAME: str = MINIO_BUCKET_NAME
    MINIO_PUBLIC_URL_OR_IP: str = MINIO_PUBLIC_URL_OR_IP

    wait_for_verification: str = wait_for_verification
    redis_om_user_creation_error: str = redis_om_user_creation_error
    email_subject: str = email_subject
    email_body: str = email_body
    temporary_token_not_found_in_headers: str = temporary_token_not_found_in_headers
    wrong_temporary_token: str = wrong_temporary_token
    code_not_found_in_body: str = code_not_found_in_body
    error_while_getting_temporary_user: str = error_while_getting_temporary_user
    wrong_verification_code: str = wrong_verification_code
    user_is_registering_with_same_email_and_username: str = user_is_registering_with_same_email_and_username
    someone_is_registering_with_same_username: str = someone_is_registering_with_same_username
    someone_is_registering_with_same_email: str = someone_is_registering_with_same_email
    username_already_exists: str = username_already_exists
    email_already_exists: str = email_already_exists


settings = Settings()
