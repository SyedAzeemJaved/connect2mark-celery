from sqlalchemy.ext.asyncio import AsyncSession

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from sqlite import models


async def get_all_attendance_tracking_by_schedule_instance_id(
    schedule_instance_id: int, db: AsyncSession
):
    result = await db.execute(
        select(models.AttendanceTrackingModel)
        .options(
            joinedload(models.AttendanceTrackingModel.user),
            joinedload(models.AttendanceTrackingModel.schedule_instance),
        )
        .where(
            models.AttendanceTrackingModel.schedule_instance_id
            == schedule_instance_id
        )
    )

    return result.scalars().all()


async def create_attendance_tracking(
    schedule_instance_id: int,
    user_id: int,
    db: AsyncSession,
):
    db_attendance_tracking = models.AttendanceTrackingModel(
        schedule_instance_id=schedule_instance_id, user_id=user_id
    )

    db.add(db_attendance_tracking)

    await db.commit()
    await db.refresh(db_attendance_tracking)

    # Eagerly load nested relationships
    result = await db.execute(
        select(models.AttendanceTrackingModel)
        .options(
            joinedload(models.AttendanceTrackingModel.user),
            joinedload(models.AttendanceTrackingModel.schedule_instance)
            .joinedload(models.ScheduleInstanceModel.teacher)
            .joinedload(models.UserModel.additional_details),
        )
        .where(models.AttendanceTrackingModel.id == db_attendance_tracking.id)
    )
    db_attendance = result.scalar_one()

    return db_attendance
