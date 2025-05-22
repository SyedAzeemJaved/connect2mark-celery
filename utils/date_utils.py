from datetime import datetime, date, timedelta, timezone

from sqlite.enums import DaysEnum

from constants import time_constants


def return_day_of_week_name(date: date | None) -> DaysEnum | None:
    """Return day of week or None"""
    if date:
        weekday = date.weekday()
        if weekday == 0:
            return DaysEnum.MONDAY
        elif weekday == 1:
            return DaysEnum.TUESDAY
        elif weekday == 2:
            return DaysEnum.WEDNESDAY
        elif weekday == 3:
            return DaysEnum.THURSDAY
        elif weekday == 4:
            return DaysEnum.FRIDAY
        elif weekday == 5:
            return DaysEnum.SATURDAY
        elif weekday == 6:
            return DaysEnum.SUNDAY
    return None


def convert_datetime_to_iso_8601_with_z_suffix(dt: datetime) -> str:
    """Convert datetime to ISO 8601 format with the Z suffix"""
    return dt.strftime(time_constants.CREATED_AND_UPDATED_AT_FORMAT)


def get_current_datetime_in_str_iso_8601_with_z_suffix() -> str:
    """Get current datetime in ISO 8601 format with the Z suffix"""
    return datetime.now(tz=timezone.utc).strftime(
        time_constants.CREATED_AND_UPDATED_AT_FORMAT
    )


def get_current_time_in_str_iso_8601(is_end_time: bool = False) -> str:
    """Get current time in ISO 8601 format (HH:MM:SS)"""
    if is_end_time:
        return datetime.strftime(
            datetime.now(tz=timezone.utc) + timedelta(hours=1),
            time_constants.START_AND_END_TIME_FORMAT,
        )
    return (
        datetime.now(tz=timezone.utc)
        .time()
        .strftime(time_constants.START_AND_END_TIME_FORMAT)
    )
