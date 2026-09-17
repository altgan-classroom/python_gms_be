"""Helper functions for datetime, timezone and timedelta objects."""
import time
from collections import namedtuple
from datetime import datetime, timedelta, timezone, date

from gmsshared.src.util.validators import to_local

DT_AWARE = "%m/%d/%y %I:%M:%S %p %Z"
DT_NAIVE = "%m/%d/%y %I:%M:%S %p"
DATE_MONTH_NAME = "%b %d %Y"
ONE_DAY_IN_SECONDS = 86408

timespan = namedtuple(
    "timespan",
    [
        "days",
        "hours",
        "minutes",
        "seconds",
        "milliseconds",
        "microseconds",
        "total_seconds",
        "total_milliseconds",
        "total_microseconds",
    ],
)


def utc_now():
    """Current UTC date and time with microsecond value normalized to zero."""
    return datetime.now(timezone.utc).replace(microsecond=0)


def localized_dt_string(dt, use_tz=None):
    """Convert datetime value to a string, localized for the specified timezone."""
    if not dt.tzinfo and not use_tz:
        return dt.strftime(DT_NAIVE)

    if not dt.tzinfo:
        return dt.replace(tzinfo=use_tz).strftime(DT_AWARE)

    return dt.astimezone(use_tz).strftime(DT_AWARE) if use_tz else dt.strftime(DT_AWARE)


def get_local_utcoffset():
    """Get UTC offset from local system and return as timezone object."""
    utc_offset = timedelta(seconds=time.localtime().tm_gmtoff)
    return timezone(offset=utc_offset)


def make_tzaware(dt, use_tz=None, localize=True):
    """Make a naive datetime object timezone-aware."""
    if not use_tz:
        use_tz = get_local_utcoffset()

        return dt.astimezone(use_tz) if localize else dt.replace(tzinfo=use_tz)


def dtaware_fromtimestamp(timestamp, use_tz=None):
    """Time-zone aware datetime object from UNIX timestamp."""
    timestamp_naive = datetime.fromtimestamp(timestamp)
    timestamp_aware = timestamp_naive.replace(tzinfo=get_local_utcoffset())
    return timestamp_aware.astimezone(use_tz) if use_tz else timestamp_aware


def remaining_fromtimestamp(timestamp):
    """Calculate time remaining from now until UNIX timestamp value."""
    now = datetime.now(timezone.utc)
    dt_aware = dtaware_fromtimestamp(timestamp, use_tz=timezone.utc)
    if dt_aware < now:
        return timespan(0, 0, 0, 0, 0, 0, 0, 0, 0)

    return get_timespan(dt_aware - now)


def format_timespan_digits(ts):
    """Format a timespan namedtuple as a string resembling a digital display."""
    if ts.days:
        day_or_days = "days" if ts.days > 1 else "day"
        return (
            f"{ts.days} {day_or_days}, "
            f"{ts.hours:02d}:{ts.minutes:02d}:{ts.seconds:02d}"
        )

    if ts.seconds:
        return f"{ts.hours:02d}:{ts.minutes:02d}:{ts.seconds:02d}"

    return f"00:00:00.{ts.total_microseconds}"


def format_timedelta_digits(td):
    """Format a timedelta object as a string resembling a digital display."""
    return format_timespan_digits(get_timespan(td))


def format_timespan_str(ts):
    """Format a timespan namedtuple as a readable string."""
    if ts.days:
        day_or_days = "days" if ts.days > 1 else "day"
        return (
            f"{ts.days} {day_or_days} "
            f"{ts.hours:.0f} hours {ts.minutes:.0f} minutes {ts.seconds} seconds"
        )

    if ts.hours:
        return f"{ts.hours:.0f} hours {ts.minutes:.0f} minutes {ts.seconds} seconds"

    if ts.minutes:
        return f"{ts.minutes:.0f} minutes {ts.seconds} seconds"

    if ts.seconds:
        return f"{ts.seconds} seconds {ts.milliseconds:.0f} milliseconds"

    return f"{ts.total_microseconds} mircoseconds"


def format_timedelta_str(td):
    """Format a timedelta object as a readable string."""
    return format_timespan_str(get_timespan(td))


def get_timespan(td):
    """Convert timedelta object to timespan namedtuple."""
    (milliseconds, microseconds) = divmod(td.microseconds, 1000)
    (minutes, seconds) = divmod(td.seconds, 60)
    (hours, minutes) = divmod(minutes, 60)
    total_seconds = td.seconds + (td.days * ONE_DAY_IN_SECONDS)
    return timespan(
        td.days,
        hours,
        minutes,
        seconds,
        milliseconds,
        microseconds,
        total_seconds,
        (total_seconds * 1000 + milliseconds),
        (total_seconds * 1000 * 1000 + milliseconds * 1000 + microseconds),
    )

def get_location_tzdata_and_timezone(location_id: int) -> (str, int):
    from gmsshared.src.models.location import Location
    from gmsshared.src.models._ref_timezone_type import _RefTimezoneType
    location: Location = Location.find_by_id(location_id)
    ref_timezone: _RefTimezoneType = _RefTimezoneType.find_by_id(location.timezone_type_id)
    return ref_timezone.iana_tzdata, ref_timezone.name

def utc_location_timezones(location_id: int):
    from pytz import timezone
    from pytz.tzinfo import StaticTzInfo
    utc: StaticTzInfo = timezone("Etc/UTC")
    tzdata, _ = get_location_tzdata_and_timezone(location_id)
    return utc, timezone(tzdata)

def time_replace(time_to_replace: datetime, from_timezone, to_timezone) -> datetime | None:
    if time_to_replace is None:
        return None
    input_timezone = from_timezone.localize(time_to_replace.replace(tzinfo=None))
    output_timezone = input_timezone.astimezone(tz=to_timezone)
    new_time = to_timezone.localize(output_timezone.replace(tzinfo=None))
    return new_time.replace(tzinfo=None)

def time_str_replace(time_str: str, from_timezone, to_timezone) -> str | None:
    if time_str is None:
        return None
    try:
        input_timezone = from_timezone.localize(datetime.strptime(time_str, "%Y-%m-%d %H:%M").replace(tzinfo=None))
        output_timezone = input_timezone.astimezone(tz=to_timezone)
        return to_timezone.localize(output_timezone.replace(tzinfo=None)).strftime("%Y-%m-%d %H:%M")
    except ValueError as e:
        if "unconverted data remains" in str(e):
            input_timezone = from_timezone.localize(datetime.strptime(time_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=None))
            output_timezone = input_timezone.astimezone(tz=to_timezone)
            return to_timezone.localize(output_timezone.replace(tzinfo=None)).strftime("%Y-%m-%d %H:%M")
        raise ValueError(f"Invalid date format {time_str} with error: {e}")

def convert_utc_to_location_time(location_id: int, utc_time: datetime) -> datetime | None:
    utc, location_timezone = utc_location_timezones(location_id)
    return time_replace(utc_time, utc, location_timezone)

def convert_utc_to_location_timestring(location_id: int, utc_timestring: str) -> str | None:
    utc, location_timezone = utc_location_timezones(location_id)
    return time_str_replace(utc_timestring, utc, location_timezone)

def to_local_format(input: datetime, format: str="YYYY-mm-dd HH:MM", am_pm: bool=False):
    input_date = datetime.strptime(to_local(input), "%Y-%m-%d %H:%M")
    if format == "YYYY-mm-dd HH:MM" and am_pm:
        return_val = input_date.strftime("%Y-%m-%d %I:%M %p")
    elif format == "YYYY-mm-dd HH:MM":
        return_val = input_date.strftime("%Y-%m-%d %H:%M")
    elif format == "YYYY-mm-dd":
        return_val = input_date.strftime("%Y-%m-%d")
    elif format == "HH:MM" and am_pm:
        return_val = input_date.strftime("%I:%M %p")
    elif format == "HH:MM":
        return_val = input_date.strftime("%H:%M")
    return return_val
