from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.time import now_in_timezone
from app.models.engagement import ReminderEvent


def fetch_due_reminders(db: Session, timezone_name: str = "Asia/Shanghai") -> list[ReminderEvent]:
    now = now_in_timezone(timezone_name)
    stmt = select(ReminderEvent).where(
        ReminderEvent.status == "pending",
        ReminderEvent.scheduled_at <= now,
    )
    return db.scalars(stmt).all()

