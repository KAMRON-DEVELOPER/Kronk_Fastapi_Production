from typing import Optional
from uuid import UUID

from app.users_app.models import UserModel
from app.users_app.schemas import LoginSchema, RegisterSchema
from bcrypt import checkpw, gensalt, hashpw
from tortoise.exceptions import DoesNotExist
from tortoise.expressions import Q


async def create_user(register_data: RegisterSchema) -> UserModel:
    try:
        hashed_password = hashpw(password=register_data.password.encode(encoding="utf-8"), salt=gensalt(rounds=8)).decode(encoding="utf-8")

        new_user = await UserModel.create(username=register_data.username, email=register_data.email, password=hashed_password)
        await new_user.save()
        return new_user
    except Exception as e:
        print(f"🌋 Exception in create_user: {e}")
        raise e


async def get_user_by_username_or_email(register_data: RegisterSchema) -> Optional[UserModel]:
    try:
        return await UserModel.filter(Q(username=register_data.username, email=register_data.email, join_type="OR")).first()
    except Exception as e:
        print(f"🌋 Exception in get_user_by_username_or_email: {e}")
        raise e


async def get_user_by_username_and_password(login_data: LoginSchema) -> UserModel:
    try:
        db_user: UserModel = await UserModel.get(username=login_data.username)

        if not checkpw(login_data.password.encode(encoding="utf-8"), db_user.password.encode(encoding="utf-8")):
            raise ValueError("Invalid password")

        return db_user
    except DoesNotExist as e:
        print(f"🌋 DoesNotExist in get_user_by_username_and_password: {e}")
        raise ValueError("User does not exist")
    except Exception as e:
        print(f"🌋 Exception in get_user_by_username_and_password: {e}")
        raise e


async def get_user_by_id(user_id: str) -> Optional[UserModel]:
    try:
        return await UserModel.get(id=user_id)
    except DoesNotExist:
        return None
    except Exception as e:
        print(f"🌋 Exception in get_user_by_id: {e}")
        raise e


async def delete_user_by_id(user_id: UUID) -> None:
    try:
        db_user: UserModel = await UserModel.get(id=user_id)
        await db_user.delete()
    except DoesNotExist:
        pass
    except Exception as e:
        print(f"🌋 Exception in delete_user_by_id: {e}")
        raise e
