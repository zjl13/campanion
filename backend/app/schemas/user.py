from pydantic import BaseModel, Field

from app.schemas.common import FocusBlock, SleepWindow, UserSummary


class PreferenceUpdateRequest(BaseModel):
    preferred_focus_blocks: list[FocusBlock] = Field(default_factory=list)
    sleep_time: SleepWindow | None = None
    timezone: str | None = None
    reminder_level: str | None = None
    preferred_style: str | None = None


class PreferenceResponse(BaseModel):
    preferred_focus_blocks: list[FocusBlock]
    sleep_time: SleepWindow | None
    timezone: str
    reminder_level: str
    preferred_style: str


class MeResponse(BaseModel):
    user: UserSummary
    preferences: PreferenceResponse | None = None
