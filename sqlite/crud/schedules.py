from datetime import datetime, date, timezone

from sqlalchemy import select, delete, or_, and_
from sqlalchemy.orm import joinedload
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import (
    ScheduleReoccurringCreateClass,
    ScheduleNonReoccurringCreateClass,
    ScheduleReoccurringUpdateClass,
    ScheduleNonReoccurringUpdateClass,
    # Search
    ScheduleReoccurringSearchClass,
    ScheduleNonReoccurringSearchClass,
)
from sqlite.enums import DaysEnum

from utils.date_utils import return_day_of_week_name


def get_all_schedules_query():
    return select(models.ScheduleModel).options(
        joinedload(models.ScheduleModel.teacher).joinedload(
            models.UserModel.additional_details
        )
    )


def get_all_schedules_by_date_query(date: date):
    return (
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(models.ScheduleModel.date == date)
    )


def get_all_schedules_by_day_query(day: DaysEnum):
    return (
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(models.ScheduleModel.day == day)
    )


def get_today_schedules_query():
    now = datetime.now(tz=timezone.utc)

    return (
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(
            or_(
                and_(
                    models.ScheduleModel.is_reoccurring.is_(True),
                    models.ScheduleModel.date.is_(None),
                    models.ScheduleModel.day
                    == return_day_of_week_name(date=now),
                ),
                and_(
                    ~models.ScheduleModel.is_reoccurring.is_(False),
                    models.ScheduleModel.date == now.date(),
                    models.ScheduleModel.day
                    == return_day_of_week_name(date=now),
                ),
            )
        )
    )


def get_all_schedules_by_user_id_query(user_id: int):
    return (
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(
            or_(
                models.ScheduleModel.academic_users.any(
                    models.UserModel.id == user_id
                ),
                models.ScheduleModel.teacher_id == user_id,
            )
        )
    )


async def get_reoccurring_schedule(
    schedule: ScheduleReoccurringSearchClass, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(
            and_(
                models.ScheduleModel.start_time_in_utc
                == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc
                == schedule.end_time_in_utc,
                models.ScheduleModel.teacher_id == schedule.teacher_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.day == schedule.day,
            )
        )
    )


async def get_non_reoccurring_schedule(
    schedule: ScheduleNonReoccurringSearchClass, db: AsyncSession
):
    return await db.scalar(
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(
            and_(
                models.ScheduleModel.start_time_in_utc
                == schedule.start_time_in_utc,
                models.ScheduleModel.end_time_in_utc
                == schedule.end_time_in_utc,
                models.ScheduleModel.teacher_id == schedule.teacher_id,
                models.ScheduleModel.location_id == schedule.location_id,
                models.ScheduleModel.date == schedule.date,
            )
        )
    )


async def get_schedule_by_id(schedule_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(models.ScheduleModel.id == schedule_id)
    )


async def create_schedule(
    schedule: (
        ScheduleReoccurringCreateClass | ScheduleNonReoccurringCreateClass
    ),
    db: AsyncSession,
):
    students = schedule.students
    del schedule.students

    if isinstance(schedule, ScheduleReoccurringCreateClass):
        db_schedule = models.ScheduleModel(
            **schedule.__dict__, is_reoccurring=True, date=None
        )
    else:
        db_schedule = models.ScheduleModel(
            **schedule.__dict__,
            is_reoccurring=False,
            day=return_day_of_week_name(date=schedule.date),
        )

    db.add(db_schedule)

    await db.commit()
    await db.refresh(db_schedule)

    # Add teacher id as user_id in ScheduleUser Model
    db.add(
        models.ScheduleUserModel(
            user_id=db_schedule.teacher_id,
            schedule_id=db_schedule.id,
        )
    )
    await db.commit()
    await db.refresh(db_schedule)

    # Add all students to the bridge table
    if students:
        user_result = await db.execute(
            select(models.UserModel).where(
                models.UserModel.id.in_(students),
                models.UserModel.is_admin.is_(False),
                models.UserModel.is_student.is_(True),
            )
        )
        student_objs = user_result.scalars().all()

        for student in student_objs:
            db.add(
                models.ScheduleUserModel(
                    user_id=student.id,
                    schedule_id=db_schedule.id,
                )
            )

        await db.commit()
        await db.refresh(db_schedule)

    # Eagerly load nested relationships
    result = await db.execute(
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(models.ScheduleModel.id == db_schedule.id)
    )
    db_schedule = result.scalar_one()

    return db_schedule


async def update_schedule(
    schedule: (
        ScheduleReoccurringUpdateClass | ScheduleNonReoccurringUpdateClass
    ),
    db_schedule: models.ScheduleModel,
    db: AsyncSession,
):
    students = schedule.students
    del schedule.students

    if isinstance(schedule, ScheduleReoccurringUpdateClass):
        db_schedule.update_reoccurring(schedule=schedule)
    else:
        db_schedule.update_non_reoccurring(
            schedule=schedule, day=return_day_of_week_name(date=schedule.date)
        )

    await db.commit()
    await db.refresh(db_schedule)

    # 1. Remove all existing students
    await db.scalars(
        delete(models.ScheduleUserModel).where(
            models.ScheduleUserModel.schedule_id == db_schedule.id
        )
    )

    # 2. Add new students
    if students:
        user_result = await db.execute(
            select(models.UserModel).where(
                models.UserModel.id.in_(students),
                models.UserModel.is_admin.is_(False),
                models.UserModel.is_student.is_(True),
            )
        )
        student_objs = user_result.scalars().all()

        for student in student_objs:
            db.add(
                models.ScheduleUserModel(
                    user_id=student.id,
                    schedule_id=db_schedule.id,
                )
            )

    await db.commit()
    await db.refresh(db_schedule)

    # Eagerly load nested relationships
    result = await db.execute(
        select(models.ScheduleModel)
        .options(
            joinedload(models.ScheduleModel.teacher).joinedload(
                models.UserModel.additional_details
            ),
        )
        .where(models.ScheduleModel.id == db_schedule.id)
    )
    db_schedule = result.scalar_one()

    return db_schedule


async def delete_schedule(db_schedule: models.ScheduleModel, db: AsyncSession):
    await db.delete(db_schedule)

    await db.commit()

    return {"detail": "Deleted successfully"}


async def get_all_students_for_a_schedule(
    db_schedule: models.ScheduleModel, db: AsyncSession
):
    result = await db.execute(
        select(models.ScheduleUserModel.user_id).where(
            models.ScheduleUserModel.schedule_id == db_schedule.id
        )
    )
    user_ids = [row[0] for row in result.fetchall()]

    if not user_ids:
        return []

    result = await db.execute(
        select(models.UserModel.id, models.UserModel.full_name).where(
            models.UserModel.id.in_(user_ids)
        )
    )
    students = [
        {"id": row[0], "full_name": row[1]} for row in result.fetchall()
    ]

    return students
