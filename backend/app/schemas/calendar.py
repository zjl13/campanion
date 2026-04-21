from datetime import date, time

from pydantic import BaseModel, Field


class CalendarBlockCreateRequest(BaseModel):
    title: str
    type: str
    weekday: int = Field(ge=1, le=7)
    start_time: time
    end_time: time
    repeat: str = "weekly"
    start_date: date | None = None
    end_date: date | None = None


class CalendarBlockResponse(BaseModel):
    id: str
    title: str
    type: str
    weekday: int
    start_time: time
    end_time: time
    repeat: str
    start_date: date | None = None
    end_date: date | None = None

