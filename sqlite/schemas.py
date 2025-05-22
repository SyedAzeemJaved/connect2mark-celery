import re
from datetime import datetime, date, time, timedelta, timezone

from fastapi import Query
from pydantic import BaseModel, ConfigDict, field_validator, model_validator

from sqlite.enums import (
    DepartmentsEnum,
    DesignationsEnum,
    DaysEnum,
    AttendanceEnum,
)

from utils.date_utils import (
    return_day_of_week_name,
    convert_datetime_to_iso_8601_with_z_suffix,
    get_current_datetime_in_str_iso_8601_with_z_suffix,
    get_current_time_in_str_iso_8601,
)

from constants import time_constants


def replace_empty_strings_with_null(cls, value):
    if isinstance(value, str):
        if value == "string" or value.strip() == "":
            return None
    return value


class Token(BaseModel):
    access_token: str
    token_type: str
    user: "User"


class TokenData(BaseModel):
    email: str | None = None


class CommonResponseClass(BaseModel):
    detail: str


# UserAdditionalDetail
class UserAdditionalDetailBaseClass(BaseModel):
    phone: str | None = None
    department: DepartmentsEnum | None = None
    designation: DesignationsEnum | None = None

    @field_validator("*", mode="after")
    @classmethod
    def replace_empty_strings_with_null(cls, value):
        return replace_empty_strings_with_null(cls=cls, value=value)


class UserAdditionalDetailCreateOrUpdateClass(UserAdditionalDetailBaseClass):
    pass


class UserAdditionalDetail(UserAdditionalDetailBaseClass):
    model_config = ConfigDict(from_attributes=True)


# User
class UserBaseClass(BaseModel):
    full_name: str
    email: str

    @field_validator("email")
    @classmethod
    def email_validator(cls, v: str) -> str:
        if " " in v:
            raise ValueError("must not contain a space")
        if "," in v:
            raise ValueError("must not contain any commas")
        if "@" not in v:
            raise ValueError("must be a valid email address")
        return v


class UserCreateClass(UserBaseClass):
    password: str
    is_admin: bool = False
    is_student: bool = False


class UserUpdateClass(UserBaseClass):
    additional_details: UserAdditionalDetailCreateOrUpdateClass | None


class UserPasswordUpdateClass(BaseModel):
    new_password: str


class User(UserBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int
    is_admin: bool = False
    is_student: bool
    additional_details: UserAdditionalDetail | None
    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )
    updated_at_in_utc: datetime | None = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )

    @model_validator(mode="after")
    def check_is_not_admin_and_student(self) -> "User":
        is_admin = self.is_admin
        is_student = self.is_student

        if is_admin and is_student:
            raise ValueError("Can not be admin and student at the same time")

        return self


# Location
class LocationBaseClass(BaseModel):
    title: str
    bluetooth_address: str
    coordinates: str

    # TODO
    # Add a validator for coordinates, as a tuple taking lat and long in degrees

    @field_validator("bluetooth_address", mode="before")
    @classmethod
    def bluetooth_address_validator(cls, v: str) -> str:
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not bool(re.match(pattern, v)):
            raise ValueError("not a valid bluetooth address")
        return v


class LocationCreateOrUpdateClass(LocationBaseClass):
    pass


class Location(LocationBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int
    secret_key: str | None  # TODO: URGENT
    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )
    updated_at_in_utc: datetime | None = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


# Schedule
class ScheduleBaseClass(BaseModel):
    title: str
    start_time_in_utc: time = get_current_time_in_str_iso_8601()
    end_time_in_utc: time = get_current_time_in_str_iso_8601(is_end_time=True)


class ScheduleCreateBaseClass(ScheduleBaseClass):
    teacher_id: int
    location_id: int
    students: list[int]


class ScheduleReoccurringCreateClass(ScheduleCreateBaseClass):
    day: DaysEnum = return_day_of_week_name(date=datetime.now(tz=timezone.utc))


class ScheduleNonReoccurringCreateClass(ScheduleCreateBaseClass):
    date: date


class ScheduleUpdateBaseClass(ScheduleBaseClass):
    teacher_id: int
    location_id: int
    students: list[int]


class ScheduleReoccurringUpdateClass(ScheduleUpdateBaseClass):
    day: DaysEnum = return_day_of_week_name(date=datetime.now(tz=timezone.utc))


class ScheduleNonReoccurringUpdateClass(ScheduleUpdateBaseClass):
    date: date


class Schedule(ScheduleBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int
    is_reoccurring: bool

    location: Location
    teacher: User

    date: date | None
    day: DaysEnum
    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )
    updated_at_in_utc: datetime | None = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


# Schedule Search
class ScheduleSearchBaseClass(BaseModel):
    teacher_id: int
    location_id: int
    start_time_in_utc: time = get_current_time_in_str_iso_8601()
    end_time_in_utc: time = get_current_time_in_str_iso_8601(is_end_time=True)


class ScheduleReoccurringSearchClass(ScheduleSearchBaseClass):
    day: DaysEnum = return_day_of_week_name(date=datetime.now(tz=timezone.utc))


class ScheduleNonReoccurringSearchClass(ScheduleSearchBaseClass):
    date: date


# Schedule Instance / Class
class ScheduleInstanceBaseClass(BaseModel):
    pass


class ScheduleInstanceUpdateClass(ScheduleInstanceBaseClass):
    teacher_id: int
    location_id: int


class ScheduleInstance(ScheduleInstanceBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int

    date: date
    start_time_in_utc: time = get_current_time_in_str_iso_8601()
    end_time_in_utc: time = get_current_time_in_str_iso_8601(is_end_time=True)

    schedule: Schedule

    location: Location
    teacher: User

    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )
    updated_at_in_utc: datetime | None = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


# Attendance
class AttendanceBaseClass(BaseModel):
    pass


class AttendanceCreateClass(AttendanceBaseClass):
    schedule_instance_id: int


class Attendance(AttendanceBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int

    schedule_instance: ScheduleInstance

    attendance_status: AttendanceEnum
    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


# Attendance Result
class AttendanceResult(AttendanceBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    schedule_instance: ScheduleInstance

    attendance_status: AttendanceEnum | None
    created_at_in_utc: datetime | None = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


class AttendanceSearchClass(BaseModel):
    start_date: date = Query(
        datetime.strftime(
            datetime.now(tz=timezone.utc) - timedelta(days=15),
            time_constants.DATE_TIME_FORMAT,
        )
    )
    end_date: date = Query(datetime.now(tz=timezone.utc).date())


# Stats
class StatsBaseClass(BaseModel):
    teachers_count: int
    students_count: int
    locations_count: int
    schedules_count: int
    schedule_instances_count: int


class TemporaryBaseClass(BaseModel):
    id: int


class TemporaryClass(TemporaryBaseClass):
    status: bool


class AttendanceTrackingBaseClass(BaseModel):
    pass


class AttendanceTrackingCreateClass(AttendanceBaseClass):
    schedule_instance_id: int


class AttendanceTracking(AttendanceTrackingBaseClass):
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: convert_datetime_to_iso_8601_with_z_suffix},
    )

    id: int

    schedule_instance: ScheduleInstance

    created_at_in_utc: datetime = (
        get_current_datetime_in_str_iso_8601_with_z_suffix()
    )


Token.model_rebuild()
