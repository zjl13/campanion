from pydantic import BaseModel


class RiskResponse(BaseModel):
    risk_score: int
    risk_level: str
    reasons: list[str]
    suggestions: list[str]


class OverviewStatsResponse(BaseModel):
    completed_tasks: int
    completion_rate: float
    checkin_rate: float
    reschedule_count: int
    current_streak_days: int
