from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict, Field


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class FocusBlock(BaseModel):
    weekday: int = Field(ge=1, le=7)
    start: str
    end: str


class SleepWindow(BaseModel):
    start: time
    end: time


class DateBoundaries(BaseModel):
    start_date: date | None = None
    end_date: date | None = None


class MessageAction(BaseModel):
    type: str
    label: str


class ProofRequirement(BaseModel):
    type: str
    hint: str


class UserSummary(ORMModel):
    id: str
    nickname: str
    timezone: str


class TaskBrief(BaseModel):
    id: str
    title: str
    status: str
    start_time: datetime
    end_time: datetime

