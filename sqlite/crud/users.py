from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import (
    UserCreateClass,
    UserUpdateClass,
    UserPasswordUpdateClass,
)
from utils.password import get_password_hash


def get_all_admin_users_query():
    return (
        select(models.UserModel)
        .where(models.UserModel.is_admin.is_(True))
        .options(joinedload(models.UserModel.additional_details))
    )


def get_all_academic_users_query(only_students: bool):
    return (
        select(models.UserModel)
        .where(
            models.UserModel.is_admin.is_(False),
            models.UserModel.is_student == only_students,
        )
        .options(joinedload(models.UserModel.additional_details))
    )


async def get_user_by_id(user_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.UserModel)
        .where(models.UserModel.id == user_id)
        .options(joinedload(models.UserModel.additional_details))
    )


async def get_user_by_email(user_email: str, db: AsyncSession):
    return await db.scalar(
        select(models.UserModel)
        .where(models.UserModel.email == user_email)
        .options(joinedload(models.UserModel.additional_details))
    )


async def get_user_by_phone(user_phone: str, db: AsyncSession):
    return await db.scalar(
        select(models.UserModel)
        .join(models.UserModel.additional_details)
        .where(models.UserAdditionalDetailModel.phone == user_phone)
        .options(joinedload(models.UserModel.additional_details))
    )


async def create_user(user: UserCreateClass, db: AsyncSession):
    user.password = get_password_hash(user.password)

    db_user = models.UserModel(**user.__dict__)

    if not user.is_admin:
        db_user.additional_details = models.UserAdditionalDetailModel(
            phone=None,
            department=None,
            designation=None,
        )
    db.add(db_user)

    await db.commit()


async def update_user(
    user: UserUpdateClass, db_user: models.UserModel, db: AsyncSession
):
    db_user.update(user)

    if db_user.additional_details:
        db_user.additional_details.update(user)

    # Need to manually update updated_at_in_utc
    # Else if only UserAdditionalDetailModel model is updated,
    #  updated_at_in_utc will not trigger
    db_user.updated_at_in_utc = datetime.now(tz=timezone.utc)

    await db.commit()


async def update_user_password(
    new_password: UserPasswordUpdateClass,
    db_user: models.UserModel,
    db: AsyncSession,
):
    new_password.new_password = get_password_hash(
        password=new_password.new_password
    )
    db_user.update_password(new_password=new_password.new_password)

    await db.commit()


async def delete_user(db_user: models.UserModel, db: AsyncSession):
    await db.delete(db_user)
    # UserAssociationDetails is on cascade, it will be deleted automatically

    await db.commit()
