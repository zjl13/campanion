from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ProofRequirement


class GoalCreateRequest(BaseModel):
    title: str
    description: str | None = None
    goal_type: str
    deadline: datetime
    priority: str = "medium"
    buddy_id: str | None = None


class GoalCreateResponse(BaseModel):
    goal_id: str
    planning_status: str


class GoalResponse(BaseModel):
    id: str
    title: str
    description: str | None = None
    goal_type: str
    priority: str
    deadline: datetime
    status: str
    buddy_id: str | None = None


class PlannedTaskResponse(BaseModel):
    id: str
    title: str
    status: str
    start_time: datetime
    end_time: datetime
    estimated_minutes: int
    proof_requirement: ProofRequirement


class GoalPlanResponse(BaseModel):
    goal_id: str
    plan_id: str
    risk_score: int
    summary: str
    tasks: list[PlannedTaskResponse]

