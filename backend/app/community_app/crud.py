from typing import Optional
from uuid import UUID

from app.users_app.models import UserModel
from app.users_app.schemas import LoginSchema, RegisterSchema
from bcrypt import checkpw, gensalt, hashpw
from fastapi import HTTPException, status
from tortoise.expressions import Q


async def get_user_by_username_or_email(register_data: RegisterSchema) -> Optional[UserModel]:
    try:
        return await UserModel.filter(
            Q(username=register_data.username, email=register_data.email, join_type="OR"),
        ).first()
    except Exception as e:
        print(f"🌋 Exception in get_user_by_username_or_email: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


async def create_user(register_data: RegisterSchema) -> UserModel:
    try:
        hashed_password = hashpw(
            password=register_data.password.encode(encoding="utf-8"),
            salt=gensalt(),
        ).decode(encoding="utf-8")

        new_user = await UserModel.create(
            username=register_data.username,
            email=register_data.email,
            phone_number=register_data.phone_number,
            password=hashed_password,
        )

        await new_user.save()

        return new_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


async def get_user_by_username_and_password(login_data: LoginSchema) -> Optional[UserModel]:
    try:
        db_user = await UserModel.filter(username=login_data.username).first()

        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username not found",
            )
        if not checkpw(login_data.password.encode(encoding="utf-8"), db_user.password.encode(encoding="utf-8")):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Password is incorrect",
            )

        return db_user
    except Exception as e:
        print(f"🌋 Exception in get_user_by_username_and_password: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


async def get_user_by_id(user_id: Optional[str]) -> Optional[UserModel]:
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User id not found",
        )
    try:
        return await UserModel.filter(id=user_id).first()
    except Exception as e:
        print(f"🌋 Exception in get_user_by_id: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )


async def delete_user_by_id(user_id: UUID) -> bool:
    try:
        user_will_be_deleted: Optional[UserModel] = await UserModel.filter(id=user_id).first()

        deleted_count = await user_will_be_deleted.delete()
        print(f"🚧 deleted_count: {deleted_count}")

        return True
    except Exception as e:
        print(f"🌋 Exception in delete_user: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"{e}",
        )
