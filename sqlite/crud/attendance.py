from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlite import models
from sqlite.enums import AttendanceEnum


async def get_attendance_by_schedule_instance_id_and_user_id(
    schedule_instance_id: int, user_id: int, db: AsyncSession
):
    return await db.scalar(
        select(models.AttendanceModel).where(
            models.AttendanceModel.schedule_instance_id == schedule_instance_id,
            models.AttendanceModel.user_id == user_id,
        )
    )


async def get_attendance_by_id(attendance_id: int, db: AsyncSession):
    return await db.scalar(
        select(models.AttendanceModel).where(
            models.AttendanceModel.id == attendance_id
        )
    )


def get_all_attendance_by_schedule_instance_ids_query(
    schedule_ids: list[int],
):
    return select(models.AttendanceModel).where(
        models.AttendanceModel.schedule_instance_id.in_(schedule_ids)
    )


async def create_attendance(
    schedule_instance_id: int,
    attendance_status: AttendanceEnum,
    user_id: int,
    db: AsyncSession,
):
    db_attendance = models.AttendanceModel(
        schedule_instance_id=schedule_instance_id,
        attendance_status=attendance_status,
        user_id=user_id,
    )

    db.add(db_attendance)

    await db.commit()
    await db.refresh(db_attendance)

    # Eagerly load nested relationships
    result = await db.execute(
        select(models.AttendanceModel)
        .options(
            joinedload(models.AttendanceModel.user),
            joinedload(models.AttendanceModel.schedule_instance)
            .joinedload(models.ScheduleInstanceModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.AttendanceModel.id == db_attendance.id)
    )
    db_attendance = result.scalar_one()

    return db_attendance
