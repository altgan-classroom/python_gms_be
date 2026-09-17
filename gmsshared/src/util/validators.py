import json
import logging
from datetime import datetime, date, timedelta
from typing import List, Any
from typing import Optional
from gmsshared.src.web.context import g

import pytz

from pydantic import BaseModel, HttpUrl
from pytz.exceptions import UnknownTimeZoneError

from gmsshared.src.util.enums import ContactTypeEnum


def dictionary_validator(value: str) -> dict | None:
    try:
        return json.loads(value)
    except Exception as e:
        logging.error(f"Error parsing value {value} with error: {e}")
        return None


def report_field_validator(value: str) -> str | None:
    if value == "-":
        return None
    return value


def attendance_report_period_validator(value: str | int) -> int:
    period_year: int
    if value == "last_twelve_months":
        return value
    try:
        period_year = int(value)
        if period_year < 1900 or period_year > 2100:
            raise ValueError(f"Invalid attendance report period year {value}")
        return period_year
    except Exception as e:
        raise ValueError(f"Invalid attendance report period with value {value}, error: {e}")


def attendance_report_month_validator(value: str) -> str:
    try:
        month_index = int(value)
        if month_index in range(13):
            return value
        else:
            raise ValueError(f"Month index {value} must be in range 1-12")
    except Exception as e:
        raise ValueError(f"Invalid attendance report month with value {value}, error: {e}")


def date_validator(value: datetime | date | str) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if value is None or isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            time: date = datetime.strptime(value, "%Y-%m-%d %H:%M").date()
            return time
        except ValueError as e:
            if "does not match format" in str(e):
                time: date = datetime.strptime(value, "%Y-%m-%d").date()
                return time
            if "unconverted data remains" in str(e):
                time: date = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").date()
                return time
            raise ValueError(f"Invalid date format {value} with error: {e}")
        except Exception as e:
            logging.error(f"Error parsing date {value} with error: {type(e)}")
            return None
    raise ValueError(f"Unknown date type {type(value)} for value {value} when validating date")


def date_format_validator(value: datetime | str) -> str | None:
    if value is None or isinstance(value, str):
        return value
    elif isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M")
    elif isinstance(value, date):
        return value.strftime("%Y-%m-%d")
    return None


def date_input_validator(value: str | datetime | None) -> datetime | None:
    if value is None or isinstance(value, datetime):
        return value
    try:
        time: datetime = datetime.strptime(value, "%Y-%m-%d %H:%M")
        return time
    except ValueError as e:
        if "unconverted data remains" in str(e):
            time: datetime = datetime.strptime(value, "%Y-%m-%d %H:%M:%S")
            return time
        raise ValueError(f"Invalid date format {value} with error: {e}")
    except Exception as e:
        logging.error(f"Error parsing date {value} with error: {type(e)}")
        return None

def validate_plans(plans: List[Any]) -> Optional[List[int]]:
    """
    Takes a list of Plans and returns a list of integers containing its IDs.
    Used as a convenience function for validation before model validation.
    """
    from gmsshared.src.models.plan import Plan
    plans_list: List[Plan] = plans
    return [p.id for p in plans_list]

def validate_class_access_group_formats(class_access_group_formats: List[Any]) -> Optional[List[int]]:
    from gmsshared.src.models._ref_plan_type import _RefPlanType
    class_access_group_formats: List[_RefPlanType] = class_access_group_formats
    return [format.id for format in class_access_group_formats]

def validate_class_access_groups(class_access_groups: List[Any]) -> List[int]:
    from gmsshared.src.models.class_access_group import ClassAccessGroup
    class_access_groups: List[ClassAccessGroup] = class_access_groups
    return [group.id for group in class_access_groups]

def validate_class(classes: List[Any]) -> List[int]:
    from gmsshared.src.models.session import Class
    classes: List[Class] = classes
    return [session.id for session in classes]

def validate_door(doors: List[Any]) -> List[int]:
    from gmsshared.src.models.door_access_door import DoorAccessDoor
    doors: List[DoorAccessDoor] = doors
    return [door.id for door in doors]

def validate_plan_type(plan_types: str) -> Optional[List[int]]:
    if plan_types is not None:
        return [p for p in plan_types.split(',')]
    else:
        return []


def check_start_and_end_times(model: BaseModel) -> BaseModel:
    model_as_dict: dict = model.model_dump()

    if (model_as_dict.get("end_date", None)
            and model_as_dict.get("start_date", None)
            and (model_as_dict["start_date"].date() > model_as_dict["end_date"].date())):
        raise ValueError('end_date must be later than start_date')

    if (model_as_dict.get("report_date_to", None)
            and model_as_dict.get("report_date_from", None)
            and (model_as_dict["report_date_from"] > model_as_dict["report_date_to"])):
        raise ValueError('report_date_to must be later than report_date_from')

    return model


def validate_contact_type(value: str | None) -> str:
    if value is None:
        return ContactTypeEnum.LEAD.value
    return value


def validate_contact_about(value: str | None) -> str:
    return value if value is not None else "No 'about' info for this user"


def payment_date_format_validator(value: datetime | str) -> str | None:
    return datetime.strftime(value, "%Y-%m-%d") if value is not None else None


def get_timezone() -> str:
    try:
        timezone = g.get("timezone")
        pytz.timezone(timezone)
    except UnknownTimeZoneError:
         timezone = "America/New_York"
    return timezone


def get_timezone_offset(timezone: str) -> int:
    timezone_object = datetime.now(pytz.timezone(timezone))
    return int(timezone_object.utcoffset().total_seconds() / 60 / 60)

def to_local_activity_history(value: date | datetime | str) -> datetime | str:
    local_timezone = pytz.timezone(get_timezone())
    utc_timezone = pytz.timezone('Etc/UTC')


    if isinstance(value, datetime):
        if value.hour == 0 and value.minute == 0 and value.second == 0 and value.microsecond == 0:
            return value.strftime("%Y-%m-%d %H:%M")

        if value.tzinfo is None:
            local_timezone_timestamp = (utc_timezone.localize(value)).astimezone(local_timezone)
        else:
            local_timezone_timestamp = value.astimezone(local_timezone)
        local_timezone_timestamp = local_timezone_timestamp.replace(tzinfo=None)
        return local_timezone_timestamp.strftime("%Y-%m-%d %H:%M")

    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')

    if value is None or isinstance(value, str):
        return value

def to_local(value: date | datetime | str) -> datetime | str:
    local_timezone = pytz.timezone(get_timezone())
    utc_timezone = pytz.timezone('Etc/UTC')

    if isinstance(value, datetime):
        if value.tzinfo is None:
            local_timezone_timestamp = (utc_timezone.localize(value)).astimezone(local_timezone)
        else:
            local_timezone_timestamp = value.astimezone(local_timezone)
        local_timezone_timestamp = local_timezone_timestamp.replace(tzinfo=None)
        return local_timezone_timestamp.strftime("%Y-%m-%d %H:%M")

    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')

    if value is None or isinstance(value, str):
        return value

def to_local_for_return_datetime_obj(value: datetime) -> datetime | None:
    local_timezone = pytz.timezone(get_timezone())
    utc_timezone = pytz.timezone('Etc/UTC')

    if isinstance(value, datetime):
        local_timezone_timestamp = (utc_timezone.localize(value)).astimezone(local_timezone)
        local_timezone_timestamp = local_timezone_timestamp.replace(tzinfo=None)
        return local_timezone_timestamp

def to_utc(value: date | datetime | str) -> datetime | str:
    local_timezone = pytz.timezone(get_timezone())
    utc_timezone = pytz.timezone('Etc/UTC')

    if isinstance(value, datetime):
        utc_timezone_timestamp = (local_timezone.localize(value)).astimezone(utc_timezone)
        utc_timezone_timestamp = utc_timezone_timestamp.replace(tzinfo=None)
        return utc_timezone_timestamp

    if isinstance(value, date):
        return value.strftime('%Y-%m-%d')

    if isinstance(value, str):
        hour, minute = value.split(':')
        todays_date_in_utc = datetime.now(utc_timezone).date()
        session_datetime = datetime(todays_date_in_utc.year, todays_date_in_utc.month,
                                    todays_date_in_utc.day, int(hour), int(minute), second=0)
        utc_timezone_timestamp = (local_timezone.localize(session_datetime)).astimezone(utc_timezone)
        utc_timezone_timestamp = utc_timezone_timestamp.replace(tzinfo=None)
        return utc_timezone_timestamp

def validate_recurrence_end_date(value: datetime | str | None) -> datetime | str | None:
    if value is not None:
        return datetime.strptime(to_local(value), "%Y-%m-%d %H:%M").strftime("%Y-%m-%d")
    return value

def normalize_local_times(old_utc: datetime, new_utc: datetime) -> datetime:
    local_timezone = pytz.timezone(get_timezone())
    utc_timezone = pytz.timezone('Etc/UTC')

    old_local = utc_timezone.localize(old_utc).astimezone(local_timezone)
    new_local = utc_timezone.localize(new_utc).astimezone(local_timezone)

    local_time = new_local.time()

    same_day_local = local_timezone.localize(
        datetime(old_local.year, old_local.month, old_local.day,
                 local_time.hour, local_time.minute, local_time.second)
    )

    result_utc = same_day_local.astimezone(pytz.utc).replace(tzinfo=None)
    return result_utc
