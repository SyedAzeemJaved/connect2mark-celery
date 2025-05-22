from datetime import datetime, date, timezone

from sqlalchemy import select, and_, or_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import ScheduleInstanceUpdateClass


def get_all_schedule_instances_query():
    return select(models.ScheduleInstanceModel).options(
        joinedload(models.ScheduleInstanceModel.teacher).joinedload(
            models.UserModel.additional_details
        ),
        joinedload(models.ScheduleInstanceModel.schedule)
        .joinedload(models.ScheduleModel.teacher)
        .joinedload(models.UserModel.additional_details),
    )


def get_all_schedule_instances_by_date_query(date: date):
    return (
        select(models.ScheduleInstanceModel)
        .options(
            joinedload(models.ScheduleInstanceModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
            joinedload(models.ScheduleInstanceModel.schedule)
            .joinedload(models.ScheduleModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.ScheduleInstanceModel.date == date)
    )


def get_all_schedule_instance_by_date_range_and_user_id_query(
    start_date: date, end_date: date, user_id: int, db: AsyncSession
):
    return (
        select(models.ScheduleInstanceModel)
        .options(
            joinedload(models.ScheduleInstanceModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
            joinedload(models.ScheduleInstanceModel.schedule)
            .joinedload(models.ScheduleModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(
            and_(
                models.ScheduleInstanceModel.date >= start_date,
                models.ScheduleInstanceModel.date <= end_date,
                or_(
                    models.ScheduleInstanceModel.academic_users.any(
                        models.UserModel.id == user_id
                    ),
                    models.ScheduleInstanceModel.teacher_id == user_id,
                ),
            )
        )
    )


def get_today_schedule_instances_query():
    now = datetime.now(tz=timezone.utc)

    return (
        select(models.ScheduleInstanceModel)
        .options(
            joinedload(models.ScheduleInstanceModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
            joinedload(models.ScheduleInstanceModel.schedule)
            .joinedload(models.ScheduleModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.ScheduleInstanceModel.date == now.date())
    )


def get_today_schedule_instances_by_user_id_query(user_id: int):

    now = datetime.now(tz=timezone.utc)

    return (
        select(models.ScheduleInstanceModel)
        .options(
            joinedload(models.ScheduleInstanceModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
            joinedload(models.ScheduleInstanceModel.schedule)
            .joinedload(models.ScheduleModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(
            and_(
                models.ScheduleInstanceModel.date == now.date(),
                or_(
                    models.ScheduleInstanceModel.academic_users.any(
                        models.UserModel.id == user_id
                    ),
                    models.ScheduleInstanceModel.teacher_id == user_id,
                ),
            )
        )
    )


async def get_schedule_instance_by_id(
    schedule_instance_id: int, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleInstanceModel)
        .options(
            joinedload(models.ScheduleInstanceModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
            joinedload(models.ScheduleInstanceModel.schedule)
            .joinedload(models.ScheduleModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.ScheduleInstanceModel.id == schedule_instance_id)
    )


async def update_schedule_instance(
    schedule_instance: ScheduleInstanceUpdateClass,
    db_schedule_instance: models.ScheduleInstanceModel,
    db: AsyncSession,
):
    db_schedule_instance.update(schedule_instance=schedule_instance)

    await db.commit()

    return db_schedule_instance


async def delete_schedule_instance(
    db_schedule_instance: models.ScheduleInstanceModel, db: AsyncSession
):
    await db.delete(db_schedule_instance)

    await db.commit()

    return {"detail": "Deleted successfully"}


async def get_all_academic_user_ids_against_a_schedule_instance(
    db_schedule_instance: models.ScheduleInstanceModel, db: AsyncSession
):
    result = await db.execute(
        select(models.ScheduleInstanceUserModel.user_id).where(
            models.ScheduleInstanceUserModel.schedule_instance_id
            == db_schedule_instance.id
        )
    )

    user_ids = result.scalars().all()

    return user_ids
