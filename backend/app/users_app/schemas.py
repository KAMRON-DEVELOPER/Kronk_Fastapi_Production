import re
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.core.minio_client import upload_file_to_minio
from app.users_app.models import CountryEnum, GenderEnum, StateOrProvinceEnum, UserModel
from app.utility.decorator import as_form
from bcrypt import checkpw, gensalt, hashpw
from fastapi import UploadFile
from pydantic import BaseModel

email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
violent_words = ["sex", "sexy", "sexual", "nude", "porn", "pornography", "nudes", "nudity"]
violent_words_regex = r"(" + "|".join(re.escape(word) for word in violent_words) + r")"


class RegisterSchema(BaseModel):
    username: Optional[str]
    email: Optional[str]
    password: Optional[str]

    async def custom_validator(self):
        if not self.username:
            raise ValueError("Username is required")
        if not (3 <= len(self.username) <= 20):
            raise ValueError("Username must be between 3 and 20 characters")

        if not self.email:
            raise ValueError("Email is required")
        if not re.match(email_regex, self.email):
            raise ValueError("Invalid email format")
        if not (5 <= len(self.email) <= 50):
            raise ValueError("Email must be between 3 and 50 characters")

        if not self.password:
            raise ValueError("Password is required")
        if not (6 <= len(self.password) <= 20):
            raise ValueError("Password must be between 6 and 20 characters.")
        if not re.search(pattern=r"\d", string=self.password):
            raise ValueError("Password must contain at least one digit.")
        if not re.search(pattern=r"[a-z]", string=self.password):
            raise ValueError("Password must contain at least one letter.")

    def __str__(self) -> str:
        return f"<🚧 RegisterSchema -> username: {self.username}, email: {self.email}, password: {self.password}>"

    def __repr__(self) -> str:
        return f"<🚧 RegisterSchema -> username: {self.username}, email: {self.email}, password: {self.password}>"


class VerifySchema(BaseModel):
    code: Optional[str]

    async def custom_validator(self):
        if not self.code:
            raise ValueError("Verification code is required")
        if not len(self.code) == 4:
            raise ValueError("Verification code must be 4 characters long")

    def __str__(self) -> str:
        return f"<🚧 VerifyModel -> code: {self.code}>"

    def __repr__(self) -> str:
        return f"<🚧 VerifyModel -> code: {self.code}>"


class LoginSchema(BaseModel):
    username: Optional[str]
    password: Optional[str]

    async def custom_validator(self):
        if not self.username:
            raise ValueError("Username is required")
        if not (3 <= len(self.username) <= 20):
            raise ValueError("Username must be between 3 and 20 characters")

        if not self.password:
            raise ValueError("Password is required")
        if not (6 <= len(self.password) <= 20):
            raise ValueError("Password must be between 6 and 20 characters.")

    def __str__(self) -> str:
        return f"<🚧 LoginModel -> username: {self.username}, password: {self.password}>"

    def __repr__(self) -> str:
        return f"<🚧 LoginModel -> username: {self.username}, password: {self.password}>"


class ProfileSchema(BaseModel):
    id: UUID
    first_name: Optional[str]
    last_name: Optional[str]
    username: str
    email: str
    avatar: Optional[str]
    banner: Optional[str]
    banner_color: Optional[str]
    birthdate: Optional[datetime]
    bio: Optional[str]
    gender: Optional[GenderEnum]
    country: Optional[CountryEnum]
    state_or_province: Optional[StateOrProvinceEnum]
    is_admin: bool
    is_blocked: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    def __str__(self) -> str:
        return f"<🚧 ProfileModel -> id: {self.id}, username: {self.username}, email: {self.email}>"

    def __repr__(self) -> str:
        return f"<🚧 ProfileModel -> id: {self.id}, username: {self.username}, email: {self.email}>"


@as_form
class UpdateSchema(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    avatar: Optional[str] = None
    banner: Optional[str] = None
    avatar_file: Optional[UploadFile] = None
    banner_file: Optional[UploadFile] = None
    birthdate: Optional[datetime] = None
    bio: Optional[str] = None
    gender: Optional[str] = None
    country: Optional[str] = None
    state_or_province: Optional[str] = None
    is_admin: Optional[bool] = False
    is_blocked: Optional[bool] = False

    async def custom_validator(self, db_user: UserModel):
        if self.first_name:
            if not (3 <= len(self.first_name) <= 20):
                raise ValueError("First name must be between 3 and 20 characters.")
            if not self.first_name.isalnum():
                raise ValueError("First name must contain only alphanumeric characters.")

        if self.last_name:
            if not (3 <= len(self.last_name) <= 20):
                raise ValueError("Last name must be between 3 and 20 characters.")
            if not self.last_name.isalnum():
                raise ValueError("Last name must contain only alphanumeric characters.")

        if self.username:
            if not (3 <= len(self.username) <= 20):
                raise ValueError("Username must be between 3 and 20 characters.")

        if self.password:
            if not (6 <= len(self.password) <= 20):
                raise ValueError("Password must be between 6 and 20 characters.")
            if not re.search(pattern=r"\d", string=self.password):
                raise ValueError("Password must contain at least one digit.")
            if not re.search(pattern=r"[a-z]", string=self.password):
                raise ValueError("Password must contain at least one letter.")
            if checkpw(self.password.encode(encoding="utf-8"), db_user.password.encode(encoding="utf-8")):
                self.password = None
            else:
                self.password = hashpw(password=self.password.encode(encoding="utf-8"), salt=gensalt(rounds=8)).decode(encoding="utf-8")

        if self.email:
            if not (3 <= len(self.email) <= 50):
                raise ValueError("Email must be between 3 and 50 characters.")
            if not re.match(email_regex, self.email):
                raise ValueError("Invalid email format.")

        if self.birthdate:
            min_age_date = datetime.now() - timedelta(days=6 * 365)
            max_age_date = datetime.now() - timedelta(days=100 * 365)
            if not (max_age_date <= self.birthdate <= min_age_date):
                raise ValueError("Birthdate must be between 6 and 100 years ago.")

        if self.bio:
            if not (3 <= len(self.bio) <= 200):
                raise ValueError("Bio must be between 3 and 200 characters.")
            if re.search(violent_words_regex, self.bio, re.IGNORECASE):
                self.bio = None
                raise ValueError("Bio contains sensitive or inappropriate content.")

        if not db_user.is_admin and ("is_admin" in self or "is_blocked" in self):
            raise ValueError("You are not admin")

        if await UserModel.filter(username=self.username, email=self.email).exists():
            raise ValueError("Username or Email already exists in the database")

        if self.gender:
            if self.gender not in GenderEnum:
                raise ValueError("Gender is not valid")
        if self.country:
            if self.country not in CountryEnum:
                raise ValueError("Country is not valid")
        if self.state_or_province:
            if self.state_or_province not in StateOrProvinceEnum:
                raise ValueError("State or Province is not valid")

        if self.avatar_file:
            avatar_url = await upload_file_to_minio(self.avatar_file, username=db_user.username)
            self.avatar = avatar_url

        if self.banner_file:
            banner_url = await upload_file_to_minio(self.banner_file, username=db_user.username)
            self.banner = banner_url

        return self

    def __str__(self):
        return f"<🚧 UpdateModel -> username: {self.username}, email: {self.email}>"

    def __repr__(self) -> str:
        return f"<🚧 UpdateModel -> username: {self.username}, email: {self.email}>"


@as_form
class TestSchema(BaseModel):
    bio: Optional[str]
    avatar: Optional[UploadFile]
    banner: UploadFile
    banner_color: str
