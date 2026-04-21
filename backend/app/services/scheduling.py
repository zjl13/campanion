from __future__ import annotations

from datetime import date, datetime, time, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import combine_with_timezone, overlaps
from app.models.engagement import ReminderEvent
from app.models.planning import CalendarBlock, Task


DEFAULT_WINDOWS = [(time(19, 0), time(21, 30))]


def parse_clock(value: str) -> time:
    return time.fromisoformat(value)


def focus_windows_for_day(user, weekday: int) -> list[tuple[time, time]]:
    preferences = getattr(user, "preferences", None)
    if preferences and preferences.focus_time_blocks:
        windows: list[tuple[time, time]] = []
        for block in preferences.focus_time_blocks:
            if int(block["weekday"]) == weekday:
                windows.append((parse_clock(str(block["start"])), parse_clock(str(block["end"]))))
        if windows:
            return windows
    return DEFAULT_WINDOWS


def calendar_blocks_for_day(
    db: Session,
    user_id: str,
    current_day: date,
    timezone_name: str,
) -> list[tuple[datetime, datetime]]:
    stmt = select(CalendarBlock).where(
        CalendarBlock.user_id == user_id,
        CalendarBlock.weekday == current_day.isoweekday(),
    )
    results = db.scalars(stmt).all()
    active_blocks: list[tuple[datetime, datetime]] = []
    for block in results:
        if block.start_date and block.start_date > current_day:
            continue
        if block.end_date and block.end_date < current_day:
            continue
        active_blocks.append(
            (
                combine_with_timezone(current_day, block.start_time, timezone_name),
                combine_with_timezone(current_day, block.end_time, timezone_name),
            )
        )
    return sorted(active_blocks, key=lambda item: item[0])


def find_open_slot(
    db: Session,
    user,
    *,
    anchor_day: date,
    duration_minutes: int,
    not_before: datetime | None = None,
    search_days: int = 14,
) -> tuple[datetime, datetime]:
    timezone_name = user.timezone
    duration = timedelta(minutes=duration_minutes)
    floor = not_before
    for offset in range(search_days):
        current_day = anchor_day + timedelta(days=offset)
        day_blocks = calendar_blocks_for_day(db, user.id, current_day, timezone_name)
        for window_start, window_end in focus_windows_for_day(user, current_day.isoweekday()):
            candidate_start = combine_with_timezone(current_day, window_start, timezone_name)
            candidate_end_limit = combine_with_timezone(current_day, window_end, timezone_name)
            if floor and candidate_start < floor:
                candidate_start = floor
            while candidate_start + duration <= candidate_end_limit:
                conflict = next(
                    (
                        (start, end)
                        for start, end in day_blocks
                        if overlaps(candidate_start, candidate_start + duration, start, end)
                    ),
                    None,
                )
                if conflict:
                    candidate_start = conflict[1]
                    continue
                return candidate_start, candidate_start + duration
    fallback_start = floor or combine_with_timezone(anchor_day, DEFAULT_WINDOWS[0][0], timezone_name)
    return fallback_start, fallback_start + duration


def create_task_reminders(db: Session, task: Task) -> list[ReminderEvent]:
    schedule = [
        ("pre_start", task.scheduled_start - timedelta(minutes=10)),
        ("start", task.scheduled_start),
        ("checkin", task.scheduled_end - timedelta(minutes=5)),
    ]
    reminders: list[ReminderEvent] = []
    for reminder_type, scheduled_at in schedule:
        reminder = ReminderEvent(
            task_id=task.id,
            reminder_type=reminder_type,
            scheduled_at=scheduled_at,
            status="pending",
            payload={
                "task_title": task.title,
                "task_id": task.id,
            },
        )
        db.add(reminder)
        reminders.append(reminder)
    return reminders


def cancel_task_reminders(db: Session, task_id: str) -> None:
    stmt = select(ReminderEvent).where(
        ReminderEvent.task_id == task_id,
        ReminderEvent.status == "pending",
    )
    for reminder in db.scalars(stmt).all():
        reminder.status = "cancelled"

