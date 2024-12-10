from random import randint
from typing import Optional

from app.core.config import jwtAccessBearer, jwtRefreshBearer, settings
from app.core.dependency import headerCredentialsDependency, jwtAccessAuthCredentialsDependency, jwtRefreshAuthCredentialsDependency
from app.core.my_redis import RegisterRedisModel
from app.users_app.crud import create_user, delete_user_by_id, get_user_by_id, get_user_by_username_and_password, get_user_by_username_or_email
from app.users_app.models import UserModel
from app.users_app.schemas import LoginSchema, RegisterSchema, UpdateSchema, VerifySchema
from app.users_app.tasks import send_email_task
from aredis_om import Migrator
from fastapi import APIRouter, Depends, HTTPException, Response, status
from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator

users_router = APIRouter()

ProfilePydantic = pydantic_model_creator(cls=UserModel)


# ! TODO register_user
@users_router.post(path="/register", status_code=status.HTTP_201_CREATED)
async def register_user(register_data: RegisterSchema, header_credentials: headerCredentialsDependency):
    try:
        await register_data.custom_validator()

        if header_credentials.temporary_token is not None:
            if await RegisterRedisModel.all_pks() and header_credentials.temporary_token in [key async for key in await RegisterRedisModel.all_pks()]:
                raise ValueError(settings.wait_for_verification)

        await Migrator.run(self=Migrator())
        if len(await RegisterRedisModel.find((RegisterRedisModel.username == register_data.username) & (RegisterRedisModel.email == register_data.email)).all()) > 0:  # noqa
            raise ValueError(settings.user_is_registering_with_same_email_and_username)
        if len(await RegisterRedisModel.find(RegisterRedisModel.username == register_data.username).all()) > 0:  # noqa
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=settings.someone_is_registering_with_same_username)
        if len(await RegisterRedisModel.find(RegisterRedisModel.email == register_data.email).all()) > 0:  # noqa
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=settings.someone_is_registering_with_same_email)

        db_user: Optional[UserModel] = await get_user_by_username_or_email(register_data=register_data)

        if db_user:
            if db_user.username == register_data.username:
                raise ValueError(settings.username_already_exists)
            if db_user.email == register_data.email:
                raise ValueError(settings.email_already_exists)

        # save register data to redis
        new_redis_om_temporary_user = RegisterRedisModel(
            code="".join([str(randint(a=0, b=9)) for _ in range(4)]),
            username=register_data.username,
            email=register_data.email,
            password=register_data.password,
        )
        await new_redis_om_temporary_user.save()
        await new_redis_om_temporary_user.expire(num_seconds=300)

        send_email_task.delay(to_email=new_redis_om_temporary_user.email, subject=settings.email_subject, body=f"{settings.email_body} {new_redis_om_temporary_user.code}")

        return {"temporary_token": new_redis_om_temporary_user.pk}
    except ValueError as e:
        print(f"🌋 ValueError in register_user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except Exception as e:
        print(f"🌋 Exception in register_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="🌋 An internal server error occurred while registering the user.")


# ! TODO verify_user
@users_router.post(path="/verify", status_code=status.HTTP_200_OK)
async def verify_user(verify_data: VerifySchema, header_credentials: headerCredentialsDependency):
    if header_credentials.temporary_token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=settings.temporary_token_not_found_in_headers)

    try:
        await verify_data.custom_validator()

        if header_credentials.temporary_token not in [key async for key in await RegisterRedisModel.all_pks()]:
            raise ValueError(f"{settings.wrong_temporary_token}")

        register_data_in_redis: RegisterRedisModel = await RegisterRedisModel.get(pk=header_credentials.temporary_token)

        if verify_data.code != register_data_in_redis.code:
            raise ValueError(f"{settings.wrong_verification_code}")

        new_user: UserModel = await create_user(register_data=RegisterSchema(**register_data_in_redis.model_dump()))

        await RegisterRedisModel.delete(pk=register_data_in_redis.pk)

        user_pydantic_model: PydanticModel = await ProfilePydantic.from_tortoise_orm(obj=new_user)
        user_dict = user_pydantic_model.model_dump(exclude_none=True)
        print(f"📝 user_dict: {user_dict}, type: {type(user_dict)}")

        return {
            "user": {**user_dict, "followers_count": await new_user.followers.all().count(), "followings_count": await new_user.followings.all().count()},  # noqa
            "access_token": settings.jwtAccessBearer.create_access_token(subject={"id": str(user_dict.get("id"))}),
            "refresh_token": settings.jwtRefreshBearer.create_refresh_token(subject={"id": str(user_dict.get("id"))}),
        }
    except ValueError as e:
        print(f"🌋 ValueError in verify_user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except Exception as e:
        print(f"🌋 Exception in verify_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="🌋 An internal server error occurred while verifying the user.")


# ! TODO login_user
@users_router.post(path="/login", status_code=status.HTTP_200_OK)
async def login_user(login_data: LoginSchema):
    try:
        await login_data.custom_validator()

        db_user: UserModel = await get_user_by_username_and_password(login_data=login_data)

        user_pydantic_model: PydanticModel = await ProfilePydantic.from_tortoise_orm(obj=db_user)
        user_dict = user_pydantic_model.model_dump(exclude_none=True)
        print(f"📝 user_dict: {user_dict}, type: {type(user_dict)}")

        return {
            "user": {**user_dict, "followers_count": await db_user.followers.all().count(), "followings_count": await db_user.followings.all().count()},  # noqa
            "access_token": settings.jwtAccessBearer.create_access_token(subject={"id": str(user_dict.get("id"))}),
            "refresh_token": settings.jwtRefreshBearer.create_refresh_token(subject={"id": str(user_dict.get("id"))}),
        }
    except ValueError as e:
        print(f"🌋 ValueError in login_user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except Exception as e:
        print(f"🌋 Exception in login_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="🌋 An internal server error occurred while logging in.")


# ! TODO get_user
@users_router.get(path="/profile", status_code=status.HTTP_200_OK)
async def get_user(credentials: jwtAccessAuthCredentialsDependency):
    try:
        db_user: Optional[UserModel] = await get_user_by_id(user_id=credentials.subject.get("id"))

        if not db_user:
            raise ValueError("User not found")

        user_pydantic_model: PydanticModel = await ProfilePydantic.from_tortoise_orm(obj=db_user)
        user_dict = user_pydantic_model.model_dump(exclude_none=True)
        print(f"📝 user_dict: {user_dict}, type: {type(user_dict)}")

        return {**user_dict, "followers_count": await db_user.followers.all().count(), "followings_count": await db_user.followings.all().count()}  # noqa
    except ValueError as e:
        print(f"🌋 ValueError in get_user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except Exception as e:
        print(f"🌋 Exception in get_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"🌋 An internal server error occurred while getting user data.")


# ! TODO update_user
@users_router.patch(path="/update", status_code=status.HTTP_200_OK)
async def update_user(credentials: jwtAccessAuthCredentialsDependency, update_data: UpdateSchema = Depends(UpdateSchema.as_form)):  # noqa
    try:
        db_user: Optional[UserModel] = await get_user_by_id(user_id=credentials.subject.get("id"))
        if not db_user:
            raise ValueError("User not found")

        # Validate update data
        await update_data.custom_validator(db_user=db_user)

        update_ready_data = update_data.model_dump(exclude_unset=True)

        # Update only if there are changes
        current_user_pydantic_model: PydanticModel = await ProfilePydantic.from_tortoise_orm(obj=db_user)
        current_user_dict = current_user_pydantic_model.model_dump(exclude_none=True)

        if any(current_user_dict.get(key) != update_ready_data.get(key) for key in update_ready_data.keys()):
            print(f"📝 update_ready_data: {update_ready_data}")
            print(f"📝 current_user_dict: {current_user_dict}")
            await db_user.update_from_dict(update_ready_data)
            await db_user.save()

        # Generate the updated profile data
        user_pydantic_model: PydanticModel = await ProfilePydantic.from_tortoise_orm(obj=db_user)
        user_dict = user_pydantic_model.model_dump(exclude_none=True)
        print(f"📝 user_dict: {user_dict}, type: {type(user_dict)}")

        return {**user_dict, "followers_count": await db_user.followers.all().count(), "followings_count": await db_user.followings.all().count()}  # noqa
    except ValueError as e:
        print(f"🌋 ValueError in update_user: {e}")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except Exception as e:
        print(f"🌋 Exception in update_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"🌋 An internal server error occurred while updating the user.")


# ! TODO delete_user
@users_router.delete(path="/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(credentials: jwtAccessAuthCredentialsDependency):
    try:
        await delete_user_by_id(user_id=credentials.subject.get("id"))
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except Exception as e:
        print(f"🌋 Exception in delete_user: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="🌋 An internal server error occurred while deleting the user.")


# ! TODO refresh
@users_router.post(path="/refresh", status_code=status.HTTP_200_OK)
async def refresh(credentials: jwtRefreshAuthCredentialsDependency):
    try:
        access_token = jwtAccessBearer.create_access_token(subject=credentials.subject)
        refresh_token = jwtRefreshBearer.create_refresh_token(subject=credentials.subject)

        return {"access_token": access_token, "refresh_token": refresh_token}
    except Exception as e:
        print(f"🌋 Exception in refresh: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"🌋 An internal server error occurred while refreshing the token.")


# ! TODO get_users
@users_router.get(path="/users", status_code=status.HTTP_200_OK)
async def get_users():
    try:
        users_model: list[UserModel] = await UserModel.all()

        if users_model:
            print(f"📝 users_model length: {len(users_model)}")
            return [(await ProfilePydantic.from_tortoise_orm(user_model)).model_dump(include={"username", "email"}) for user_model in users_model]

        return []
    except Exception as e:
        print(f"🌋 Exception in get_users: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"🌋 An internal server error occurred while getting the users.")


# ! TODO delete_all_users
@users_router.delete(path="/delete_all_users", status_code=status.HTTP_204_NO_CONTENT)
async def delete_all_users():
    await UserModel.all().delete()
    return {"message": "All users deleted. 🗑️"}
