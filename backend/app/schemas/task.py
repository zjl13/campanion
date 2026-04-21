from datetime import datetime

from pydantic import BaseModel

from app.schemas.common import ProofRequirement


class TaskDetailResponse(BaseModel):
    id: str
    goal_id: str
    title: str
    description: str | None = None
    status: str
    start_time: datetime
    end_time: datetime
    estimated_minutes: int
    actual_minutes: int | None = None
    proof_requirement: ProofRequirement
    completion_note: str | None = None


class TaskCompleteRequest(BaseModel):
    completion_note: str | None = None


class TaskStartResponse(BaseModel):
    task_id: str
    status: str


class TodayTasksResponse(BaseModel):
    date: str
    tasks: list[TaskDetailResponse]


class TaskRescheduleRequest(BaseModel):
    reason_text: str
    preferred_strategy: str = "auto"


class TaskRescheduleResponse(BaseModel):
    result: str
    reason_category: str
    new_task: dict[str, object]
    assistant_reply: str

