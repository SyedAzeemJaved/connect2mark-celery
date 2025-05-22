from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from sqlite import models
from sqlite.schemas import StatsBaseClass


async def get_all_stats(db: AsyncSession):
    teachers_count = await db.scalar(
        select(func.count())
        .select_from(models.UserModel)
        .where(
            models.UserModel.is_admin.is_(False),
            models.UserModel.is_student.is_(False),
        )
    )
    students_count = await db.scalar(
        select(func.count())
        .select_from(models.UserModel)
        .where(
            models.UserModel.is_admin.is_(False),
            models.UserModel.is_student.is_(True),
        )
    )

    location_count = await db.scalar(
        select(func.count()).select_from(models.LocationModel)
    )
    schedules_count = await db.scalar(
        select(func.count()).select_from(models.ScheduleModel)
    )
    schedule_instances_count = await db.scalar(
        select(func.count()).select_from(models.ScheduleInstanceModel)
    )

    return StatsBaseClass(
        teachers_count=teachers_count if teachers_count else 0,
        students_count=students_count if students_count else 0,
        locations_count=location_count if location_count else 0,
        schedules_count=schedules_count if schedules_count else 0,
        schedule_instances_count=(
            schedule_instances_count if schedule_instances_count else 0
        ),
    )
