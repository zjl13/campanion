from datetime import date, datetime, time, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


FALLBACK_TIMEZONES = {
    "Asia/Shanghai": timezone(timedelta(hours=8)),
    "UTC": timezone.utc,
}


def resolve_timezone(timezone_name: str):
    try:
        return ZoneInfo(timezone_name)
    except ZoneInfoNotFoundError:
        return FALLBACK_TIMEZONES.get(timezone_name, timezone.utc)


def ensure_timezone(value: datetime, timezone_name: str) -> datetime:
    zone = resolve_timezone(timezone_name)
    if value.tzinfo is None:
        return value.replace(tzinfo=zone)
    return value.astimezone(zone)


def now_in_timezone(timezone_name: str) -> datetime:
    return datetime.now(resolve_timezone(timezone_name))


def combine_with_timezone(day: date, value: time, timezone_name: str) -> datetime:
    return datetime.combine(day, value).replace(tzinfo=resolve_timezone(timezone_name))


def overlaps(
    start_a: datetime,
    end_a: datetime,
    start_b: datetime,
    end_b: datetime,
) -> bool:
    return start_a < end_b and start_b < end_a


def clamp_datetime_floor(value: datetime, floor: datetime) -> datetime:
    return value if value >= floor else floor


def minutes_to_timedelta(minutes: int) -> timedelta:
    return timedelta(minutes=minutes)
