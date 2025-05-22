from celery import Celery, schedules as celery_schedules

from datetime import datetime, date, timezone

from sqlalchemy import create_engine, select, and_
from sqlalchemy.orm import sessionmaker, Session

from secret import secret

from sqlite.models import (
    ScheduleUserModel,
    ScheduleInstanceModel,
    ScheduleInstanceUserModel,
)

from sqlite.crud import schedules


FILE_NAME = __name__

celery = Celery(
    FILE_NAME,
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
)

sync_engine = create_engine(secret.SYNC_DATABASE_URL)
SyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=sync_engine
)


def get_exact_schedule_instance(
    schedule_id: int,
    teacher_id: int,
    location_id,
    date: date | None,
    start_time_in_utc: datetime,
    end_time_in_utc: datetime,
    db: Session,
):
    return db.execute(
        select(ScheduleInstanceModel).where(
            and_(
                ScheduleInstanceModel.schedule_id == schedule_id,
                ScheduleInstanceModel.teacher_id == teacher_id,
                ScheduleInstanceModel.location_id == location_id,
                ScheduleInstanceModel.date == date,
                ScheduleInstanceModel.start_time_in_utc == start_time_in_utc,
                ScheduleInstanceModel.end_time_in_utc == end_time_in_utc,
            )
        )
    ).scalar_one_or_none()


@celery.task
def create_schedule_instances_or_classes() -> None:
    with SyncSessionLocal() as db:
        try:
            today_schedules_query = schedules.get_today_schedules_query()
            result = db.execute(today_schedules_query)
            db_today_schedules = [row[0] for row in result.fetchall()]

            now = datetime.now(tz=timezone.utc)

            for schedule in db_today_schedules:
                result = db.execute(
                    select(ScheduleUserModel.user_id)
                    .where(ScheduleUserModel.schedule_id == schedule.id)
                    .distinct()
                )
                both_student_teacher_ids = [row[0] for row in result.fetchall()]

                db_schedule_instance = ScheduleInstanceModel(
                    schedule_id=schedule.id,
                    teacher_id=schedule.teacher_id,
                    location_id=schedule.location_id,
                    date=(
                        now.date()
                        if schedule.is_reoccurring and schedule.date is None
                        else schedule.date
                    ),
                    start_time_in_utc=schedule.start_time_in_utc,
                    end_time_in_utc=schedule.end_time_in_utc,
                )

                has_other = get_exact_schedule_instance(
                    schedule_id=db_schedule_instance.schedule_id,
                    teacher_id=db_schedule_instance.teacher_id,
                    location_id=db_schedule_instance.location_id,
                    date=db_schedule_instance.date,
                    start_time_in_utc=db_schedule_instance.start_time_in_utc,
                    end_time_in_utc=db_schedule_instance.end_time_in_utc,
                    db=db,
                )

                if not has_other:
                    db.add(db_schedule_instance)
                    db.commit()

                    for academic_user_id in both_student_teacher_ids:
                        db_schedule_instance_user = ScheduleInstanceUserModel(
                            user_id=academic_user_id,
                            schedule_instance_id=db_schedule_instance.id,
                        )
                        db.add(db_schedule_instance_user)
                        db.commit()
        except Exception as e:
            print("There seems to be an error")
            print(e)


# Schedule the task
celery.conf.beat_schedule = {
    "task-every-20-seconds": {
        "task": f"{FILE_NAME}.create_schedule_instances_or_classes",
        "schedule": 20.0,  # Run every 20 seconds
    },
}

# celery -A celery_worker.celery worker -B --loglevel=info
# docker run -d --name redis -p 6379:6379 redis
