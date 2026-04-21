from datetime import timedelta

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.api.serializers import serialize_task
from app.core.time import now_in_timezone
from app.db.session import get_db
from app.models.planning import Task
from app.models.user import User
from app.schemas.proof import ProofUploadResponse
from app.schemas.task import (
    TaskCompleteRequest,
    TaskDetailResponse,
    TaskRescheduleRequest,
    TaskRescheduleResponse,
    TaskStartResponse,
    TodayTasksResponse,
)
from app.services.chat_service import create_message
from app.services.proof_review import submit_proof
from app.services.rescheduler import reschedule_task


router = APIRouter(prefix="/tasks", tags=["tasks"])


def ensure_task_owner(task: Task | None, user_id: str) -> Task:
    if not task or task.goal.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


@router.get("/today", response_model=TodayTasksResponse)
def get_today_tasks(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TodayTasksResponse:
    now = now_in_timezone(current_user.timezone)
    day_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=1)
    tasks = db.scalars(
        select(Task)
        .join(Task.goal)
        .where(
            Task.scheduled_start >= day_start,
            Task.scheduled_start < day_end,
            Task.status.in_(["scheduled", "active", "completed", "rescheduled"]),
        )
        .order_by(Task.scheduled_start.asc())
    ).all()
    tasks = [task for task in tasks if task.goal.user_id == current_user.id]
    return TodayTasksResponse(
        date=day_start.date().isoformat(),
        tasks=[serialize_task(task) for task in tasks],
    )


@router.get("/{task_id}", response_model=TaskDetailResponse)
def get_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskDetailResponse:
    task = ensure_task_owner(db.get(Task, task_id), current_user.id)
    return TaskDetailResponse.model_validate(serialize_task(task))


@router.post("/{task_id}/start", response_model=TaskStartResponse)
def start_task(
    task_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskStartResponse:
    task = ensure_task_owner(db.get(Task, task_id), current_user.id)
    task.status = "active"
    db.commit()
    return TaskStartResponse(task_id=task.id, status=task.status)


@router.post("/{task_id}/complete", response_model=TaskDetailResponse)
def complete_task(
    task_id: str,
    payload: TaskCompleteRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskDetailResponse:
    task = ensure_task_owner(db.get(Task, task_id), current_user.id)
    task.status = "completed"
    task.completion_note = payload.completion_note
    create_message(
        db,
        user_id=current_user.id,
        buddy_id=task.goal.buddy_id,
        role="assistant",
        content="我先把这次完成记上了，之后记得补一下证明材料会更完整。",
        message_type="checkin_feedback",
        related_goal_id=task.goal_id,
        related_task_id=task.id,
    )
    db.commit()
    db.refresh(task)
    return TaskDetailResponse.model_validate(serialize_task(task))


@router.post("/{task_id}/reschedule", response_model=TaskRescheduleResponse)
def reschedule(
    task_id: str,
    payload: TaskRescheduleRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> TaskRescheduleResponse:
    task = ensure_task_owner(db.get(Task, task_id), current_user.id)
    _, new_task, assistant_reply, category = reschedule_task(
        db,
        user=current_user,
        task=task,
        reason_text=payload.reason_text,
        preferred_strategy=payload.preferred_strategy,
    )
    db.commit()
    return TaskRescheduleResponse(
        result="rescheduled",
        reason_category=category,
        new_task={
            "id": new_task.id,
            "start_time": new_task.scheduled_start,
            "end_time": new_task.scheduled_end,
        },
        assistant_reply=assistant_reply,
    )


@router.post("/{task_id}/proofs", response_model=ProofUploadResponse)
async def upload_proof(
    task_id: str,
    file: UploadFile | None = File(default=None),
    text_note: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ProofUploadResponse:
    task = ensure_task_owner(db.get(Task, task_id), current_user.id)
    file_bytes = await file.read() if file else None
    proof, _ = submit_proof(
        db,
        user=current_user,
        task=task,
        filename=file.filename if file else None,
        file_bytes=file_bytes,
        text_note=text_note,
    )
    db.commit()
    return ProofUploadResponse(proof_id=proof.id, review_status="pending_review")
